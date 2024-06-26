from . import *
from .models import FAQ, UserQuery, User
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv


# Apply the generate_tags function to create the 'tags' column of all the current question and answer if tags are not added
def generateAllTags():
    if 'tags' not in faq_database.columns:
        faq_database['tags'] = faq_database.apply(lambda row: generate_tags(row['questions'], row['answers']), axis=1)
        faq_database.to_csv(faq_database_csv_path, index=False)


# initializing vectorizer
vectorizer = TfidfVectorizer()

# Fit and transform the tags of stored queries in faq database
stored_tags_vector = vectorizer.fit_transform(faq_database['tags'])


def check_if_answer_already_exists_in_faq_database(answer_to_check):
    # Check if the answer exists in the specified column
    answer_exists = any(faq_database["faq_answer"] == answer_to_check)
    return answer_exists


#if you want to add faq query to faq database csv file
def save_faq_to_faq_database(faq_question, faq_answer):

    global stored_tags_vector
    faq_tags = generate_tags(faq_question, faq_answer)
    new_faq_data = {'faq_question': faq_question, 'faq_answer': faq_answer, 'tags': faq_tags}
    # Add the new row using loc[]
    faq_database.loc[len(faq_database)] = new_faq_data
    faq_database.to_csv(faq_database_csv_path, index=False)
    stored_tags_vector = vectorizer.fit_transform(faq_database['tags'])


# if you want to add faq query to faq database
def add_query_to_faq_database(faq_question, faq_answer):
    faq_tags = generate_tags(faq_question, faq_answer)
    new_faq_data = FAQ.objects.create(
        faq_question=faq_question,
        faq_answer=faq_answer,
        faq_tags=faq_tags,
        creation_time=timezone.now(),
        updation_time=timezone.now()
    )

    new_faq_data.save()


def integrate_faq_database(faq_database):
    for faq in faq_database:
        save_faq_to_faq_database(faq['question'], faq['answer'])


def handle_user_feedback(user_query, bot_response, user_feedback_for_last_response):
    global is_feedback_required_for_current_response

    if user_feedback_for_last_response == 'like':

        # saving the response of the faq if it is given by doubt assistant and user is satisfied with it
        if user_query and bot_response and not check_if_answer_already_exists_in_faq_database(bot_response):
            # print(user_query)
            # print(bot_response)
            save_faq_to_faq_database(user_query, bot_response)

        # ending the session as the user is satisfied by not taking feedback
        is_feedback_required_for_current_response = "No"

        return random.choice(positive_feedback_responses) + " " + feedback_suffix

    elif user_feedback_for_last_response == 'dislike':
        # user is not satisfied so falling back the user query to the doubt assistant
        return fallback_to_doubt_assistant(user_query, bot_response, user_feedback_for_last_response)

    else:
        # this is not a user feedback, it is a user query so for this getting response from our faq database
        return get_response_from_faq_database(user_query)


def get_response_from_faq_database(user_query):
    # using global variable
    global is_feedback_required_for_current_response

    # user query preprocessing
    preprocessed_user_query = preprocess_text(user_query)

    # Transform user query
    user_query_vector = vectorizer.transform([preprocessed_user_query])

    # Calculate cosine similarity with each stored faq
    similarities = cosine_similarity(user_query_vector, stored_tags_vector)

    # Find the most similar faq's index and similarity score
    most_similar_index = similarities.argmax()
    most_similar_score = similarities[0][most_similar_index]

    if most_similar_score < threshold_value:

        is_feedback_required_for_current_response = "No"

        if find_pattern(greeting_pattern, user_query):
            return if_user_message_contains_greeting
        elif find_pattern(exit_pattern, user_query):
            return if_user_message_contains_exit_message
        elif find_pattern(thanking_pattern, user_query):
            return random.choice(positive_feedback_responses) + " " + feedback_suffix
        else:
            # fallback to doubt assistant
            doubt_assistants_response = fallback_to_doubt_assistant(user_query, "", "")
            return doubt_assistants_response
    else:
        is_feedback_required_for_current_response = "Yes"
        return faq_database['faq_answer'][most_similar_index]


# This is the function for falling back to doubt assistant we can include doubt assistant as per our
# requirements and availablity for now I am just keeping it simple and returning a static response.
def fallback_to_doubt_assistant(user_query, bot_response, user_feedback):
    # as right now we don't have any doubt assistant in the backend to solve the query that's why we are giving this static response and setting
    # feedback as not required for now but when the doubt assistant will be their we can easily send their response and set feedback required to True for taking user feedback

    global is_feedback_required_for_current_response

    # when their will be a doubt assistant to respond we will get their response and set the is_feedback_required_for_current_response variable as "Yes"
    is_feedback_required_for_current_response = "No"

    return "Sorry! I am unable to understand you. So I am, sending your query to a doubt assistant. Your query will be resolved by doubt assistant very sortly."


def index(request):
    return render(request, "chatbotapp/index.html")


def chatbot(request):
    if request.method == 'GET':

        # generating tags for all the questions and answers
        generateAllTags()

        user_query = request.GET.get('userQuery')
        user_feedback_for_last_response = request.GET.get('userFeedback')
        bot_response = request.GET.get('botResponse')

        response = handle_user_feedback(user_query, bot_response, user_feedback_for_last_response)

        return JsonResponse(
            {'response': response, 'isUserFeedbackRequiredForThisResponse': is_feedback_required_for_current_response})
    else:
        return JsonResponse({'error': 'Only GET requests are allowed for this endpoint.'})


# this is for sharing user details present in User table and all the queries asked by them
# you have to pass the time value for how much last hours do you want the data
def share_user_data_with_sales_team(request):
    # This variable is passed in the request and is used to retrive the queries came in last this much hours mention
    # by the variable
    last_hours = request.GET.get['lastHours']

    # Get the current datetime
    now = timezone.now()

    # Calculate the datetime based on the last N hours
    start_datetime = now - timedelta(hours=last_hours)

    # fetching all users
    users = User.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data_and_their_queries.csv"'

    writer = csv.writer(response)

    # Write user data and their queries header row
    writer.writerow(['user_id', 'user_name', 'user_email', 'user_contact_number', 'user_queries'])

    # Write user data rows
    for user in users:
        # fetching all the queries asked by this user
        user_queries = fetch_user_queries_of_an_user(start_datetime, user.user_id)
        # writing the data
        writer.writerow([user.user_id, user.user_name, user.user_email, user.user_contact_number, user_queries])

    return response


# this is the performace monitor for getting all the necessary data of all the user queries came in mentioned last hours
# it will return a csv file containing all the field of UserQuery model
def performance_monitor(request):
    # This variable is passed in the request and is used to retrive the queries came in last this much hours mention
    # by the variable
    last_hours = request.GET.get['lastHours']

    # Get the current datetime
    now = timezone.now()

    # Calculate the datetime based on the last N hours
    start_datetime = now - timedelta(hours=last_hours)

    # Query the database for data within the specified timeframe
    queryset = UserQuery.objects.filter(creation_time__gte=start_datetime)

    # Prepare response headers for CSV file download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_queries_of_last_{last_hours}_hours.csv"'

    # Create a CSV writer
    csv_writer = csv.writer(response)

    # Write the header row
    csv_writer.writerow(['query_id', 'user_query', 'user_id', 'is_query_resolved', 'query_resolved_by',
                         'response_given', 'time_taken_to_solve_query', 'creation_time', 'last_updation_time'])

    # Write data rows to the CSV file
    for query in queryset:
        csv_writer.writerow([
            query.query_id,
            query.user_query,
            query.user_id,
            query.is_query_resolved,
            query.query_resolved_by,
            query.response_given,
            query.time_taken_to_solve_query,
            query.creation_time,
            query.updation_time
        ])

    return response


# for fetching user queries of a perticular user in last given hours
def fetch_user_queries_of_an_user(start_datetime, user_id):
    # Get all user queries for the specified user_id and from the given start time.
    user_queries = UserQuery.objects.filter(user_id=user_id, creation_time__gte=start_datetime).values_list(
        'user_query', flat=True)

    # Convert the queryset to a list
    user_query_list = list(user_queries)

    return ' '.join(user_query_list)
