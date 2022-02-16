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
    def __init__(self, path):
        with open(path, 'r') as file:
            self.questions = yaml.safe_load(file)
        
        self.question_numbers = [k for k in self.questions]
        self.current_question = ""
        self.current_question_number = ""
        self.current_explanation = "No explanation found. Click on New Question to retrieve a new question."
        self.current_example = "No example found. Click on New Question to retrieve a new question."
    
    def update_random_question(self):
        question = random.choice(self.question_numbers)
        self.current_question_number = question
        self.current_question = self.questions[question]['question']
        self.current_example = self.questions[question]['example']
        self.current_explanation = self.questions[question]['explanation']
        self.question_numbers.remove(question)

class Answers():
    def __init__(self, path):
        self.filepath = path
        try:
            with open(path, 'r') as file:
                self.answers = yaml.safe_load(file)
        except:
            print('Error opening answers file. Make sure it is set in the correct path')
            self.answers= None


    def retrieve_answer(self, question_number):
        return self.answers.get(question_number, "")
    
    def save_answer(self, question_number, text):
        try:
            with open(self.filepath, 'r') as file:
                answers = yaml.safe_load(file)
            
            answers[question_number] = text

            with open(self.filepath, 'w') as file:
                yaml.safe_dump(answers, file)
                    
        except:
            print("There was a problem trying to save the new answer into the file.")


question = Questions('interviewquestions.yaml')
answer = Answers('answers.yaml')

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def homepage():

    def say(text):
        os.system(f'say "{text}"')
     
    if request.method == 'POST':
        print("Some test here first")
        if request.form['askquestion'] == 'save':
            print("Some test here second")
            print(request.form['askquestion'])
        if request.form['askquestion'] == 'New Question':
            question.update_random_question()
            t = Thread(target=say, args=(question.current_question,))
            t.start()
            return render_template('index.html', question=question.current_question)
        if request.form['askquestion'] == 'Example':
            t = Thread(target=say, args=(question.current_example,))
            t.start()
            return render_template('index.html', question=question.current_question, example=question.current_example)
        if request.form['askquestion'] == 'Explanation':
            t = Thread(target=say, args=(question.current_explanation,))
            t.start()
            return render_template('index.html', question=question.current_question, explanation=question.current_explanation)
        return render_template('index.html')
    else:
        return render_template('index.html')

@app.route("/store-answer", methods=["POST", "GET"])
@cross_origin()
def storeAnswer(): 
    text = request.form["save"]
    answer.save_answer(question.current_question_number, text)
    return render_template('index.html',
                            question=question.current_question, 
                            answer=text)

if __name__ == "__main__":
    app.run(port=8000, debug=True, threaded=True)