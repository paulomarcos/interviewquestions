# -*- coding: utf-8 -*-

"""
 @brief   Interview Questions 
 @author  Paulo Dores
 @date    Feb 16th 2022
 @license MIT
 Copyright (c) 2022 Paulo Dores
"""
import os
from threading import Thread
from flask_cors import cross_origin
from flask import Flask, render_template, request
import random
import yaml


app = Flask(__name__)

class Questions():
    """ Class that handles the questions by fetching and storing it
        on the appropriate file.

        @param path : <str> Relative or absolute path to the yaml file
    """
    def __init__(self, path):
        with open(path, 'r') as file:
            self.questions = yaml.safe_load(file)
        
        self.question_numbers = [k for k in self.questions]
        self.current_question = ""
        self.current_question_number = ""
        self.current_explanation = "No explanation found. Click on New Question to retrieve a new question."
        self.current_example = "No example found. Click on New Question to retrieve a new question."
    
    def update_random_question(self):
        if len(self.question_numbers) <= 0:
            self.question_numbers = [k for k in self.questions]
        question = random.choice(self.question_numbers)
        self.current_question_number = question
        self.current_question = self.questions[question]['question']
        self.current_example = self.questions[question]['example']
        self.current_explanation = self.questions[question]['explanation']
        self.question_numbers.remove(question)

class Answers():
    """ Class that handles the answers by fetching and storing it
        on the appropriate file.

        @param path : <str> Relative or absolute path to the yaml file
    """
    def __init__(self, path):
        self.filepath = path
        self.answers = ""
        self.update_answers()
        self.cached_answer = ""

    def retrieve_answer(self, question_number, new=False):
        if self.cached_answer != "" and not new:
            return self.cached_answer
        return self.answers.get(question_number, "")
    
    def update_answers(self):
        try:
            with open(self.filepath, 'r') as file:
                self.answers = yaml.safe_load(file)
        except:
            print('Error opening answers file. Make sure it is set in the correct path')
            self.answers= None
    
    def update_cache(self, text):
        self.cached_answer = text
        print(self.cached_answer, text)
    
    def save_answer(self, question_number, text):
        try:
            with open(self.filepath, 'r') as file:
                answers = yaml.safe_load(file)
            
            answers[question_number] = text

            with open(self.filepath, 'w') as file:
                yaml.safe_dump(answers, file)
            
            self.update_answers()
                    
        except:
            print("There was a problem trying to save the new answer into the file.")


def say(text: str):
    """ Method to initiate the 'say' function on the system.
     ** ONLY WORKS ON MACOS **
     @param text: <string>
    """
    os.system(f'say "{text}"')


def process_answer(request_form):
    """ Processes the answer form. 
        @param request_form = request.form <ImmutableMultiDict>
        @return template
    """

    if request_form.get('savebutton') == 'Save':
        text = request_form.get("save")
        answer.save_answer(question.current_question_number, text)
        return render_template('index.html',
                                question=question.current_question, 
                                answer=text)

    if request_form.get('savebutton') == 'Show Answer':
        text = request_form.get("save")
        if  text == "":
            text = answer.retrieve_answer(question.current_question_number)
        return render_template('index.html',
                                question=question.current_question, 
                                answer=text)

    if request_form.get('savebutton') == 'Hide Answer':
        answer.update_cache(request.form.get("save"))   
        return render_template('index.html',
                                question=question.current_question)  

    return render_template('index.html',
                           question=question.current_question,)


def process_question(request_form):
    """ Processes the question form. 
        @param request_form = request.form <ImmutableMultiDict>
        @return template
    """

    if request_form.get('askquestion') == 'New Question':
        question.update_random_question()
        t = Thread(target=say, args=(question.current_question,))
        t.start()
        return render_template('index.html', 
                                question=question.current_question, 
                                answer=answer.retrieve_answer(question.current_question_number, new=True))

    if request_form.get('askquestion') == 'Example':
        t = Thread(target=say, args=(question.current_example,))
        t.start()
        return render_template('index.html', 
                                question=question.current_question, 
                                example=question.current_example, 
                                answer=answer.cached_answer)

    if request_form.get('askquestion') == 'Explanation':
        t = Thread(target=say, args=(question.current_explanation,))
        t.start()
        return render_template('index.html', 
                                question=question.current_question, 
                                explanation=question.current_explanation, 
                                answer=answer.cached_answer)
    
    return render_template('index.html')


question = Questions('interviewquestions.yaml')
answer = Answers('answers.yaml')

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def homepage():
     
    if request.method == 'POST':
        question_form = request.form.get('askquestion', None)
        return process_question(request.form) if question_form else process_answer(request.form)

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True, threaded=True)