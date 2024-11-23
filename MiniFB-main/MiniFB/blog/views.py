from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from django.http import JsonResponse
from .wit_service import query_wit_ai


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def wit_ai_view(request):
    message = request.GET.get('message', '').lower().strip()  # Normalize the input message
    if message:
        # Predefined utterances mapping to responses
        predefined_utterances = {
            "hello": "Hello! How can I assist you today?",
            "what can you do?": "I can help with various tasks like answering questions, checking weather, or managing timers. How can I help you?",
            "hey": "Hey there! What can I do for you?",
            "hello there": "Hi! How can I assist you?",
            "what's on your mind?": "I'm here to assist you. Feel free to ask anything!",
            "can you help me?": "Absolutely! What do you need help with?",
            "good day": "Good day to you! How can I help?",
            "hi": "Hi! What can I do for you today?",
            "what is the weather today?": "Let me check the weather for you. Can you specify a location?",
            "good morning": "Good morning! Hope you have a great day ahead. How can I assist?",
            "what is this project all about?": "This Project is made by Bryan Kim Calipes as part of their project in the course Integrative Programming.",
            "what is this project about?": "This Project is made by Bryan Kim Calipes as part of their project in the course Integrative Programming.",
            "who is bryan's girlfriend?": "Bryan's Girlfriend is Ritchel Obligado"  # Correct mapping for this query
        }

        # Check for a predefined response first
        if message in predefined_utterances:
            return JsonResponse({'reply': predefined_utterances[message]})

        # Query the Wit.ai API with the message
        response_data = query_wit_ai(message)
        
        # Check if there was an error in the response
        if 'error' in response_data:
            return JsonResponse({'error': response_data['error']}, status=400)

        # Extract the intents, entities, and traits from the Wit.ai response
        intents = response_data.get('intents', [])
        entities = response_data.get('entities', {})
        traits = response_data.get('traits', {})

        # Default response message
        reply = "Sorry, I didn't understand that."

        # Process intents
        if intents:
            top_intent = intents[0]  # Get the most confident intent
            intent_name = top_intent.get('name')
            confidence = top_intent.get('confidence', 0)

            # Handle specific intents based on the name
            if intent_name == 'greetings' and confidence > 0.7:
                reply = "Hello! How can I assist you today?"
            elif intent_name == 'help' and confidence > 0.7:
                reply = "Sure! I can help you. What do you need assistance with?"
            elif intent_name == 'wit/add_time_timer' and confidence > 0.7:
                reply = "Timer feature isn't implemented yet, but I can guide you!"

        # Process entities
        if entities:
            if 'wit/location' in entities:
                location = entities['wit/location'][0].get('value')
                reply = f"Got it! You're asking about {location}. Let me check that for you."

            elif 'wit/amount_of_money' in entities:
                amount = entities['wit/amount_of_money'][0].get('value')
                reply = f"You're inquiring about an amount of {amount}. Can you clarify?"

        # Process traits
        if traits:
            if 'wit/sentiment' in traits:
                sentiment = traits['wit/sentiment'][0].get('value')
                if sentiment == 'positive':
                    reply += " I'm glad you're feeling positive!"
                elif sentiment == 'negative':
                    reply += " I'm here to help if you're feeling down."

            if 'wit/thanks' in traits:
                reply = "You're welcome! Let me know if you have more questions."

        # Return the response as a JSON object
        return JsonResponse({'reply': reply})

    else:
        return JsonResponse({'error': 'No message provided'}, status=400)
