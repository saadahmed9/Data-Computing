from flask import Flask,render_template,request,flash,redirect, url_for
import numpy as np
# import pickle5 as pickle
import pickle
import ast
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
model = pickle.load(open('lr_model.pkl', 'rb'))


app.secret_key = "123456"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict',methods=["POST","GET"])
def predict():

    form_data = {}
    form_data['isalc'] = request.form['isalc']
    form_data['drugs'] = request.form['drugs']
    form_data['poverty'] = request.form['poverty']

    print("form data is ",form_data )

    inp_bmi = float(request.form['bmi'])

    inp_age = int(request.form['age'])

    inp_sex = int(request.form['sex'])

    inp_marital = int(request.form['marital_status'])

    inp_alc = int(request.form['isalc'])

    inp_drg = int(request.form['drugs'])

    inp_fam = int(request.form['fam_people'])

    inp_school = int(request.form['school'])

    inp_diab= int(request.form['diabetic'])

    inp_poverty = float(request.form['poverty'])

    is_healthy, is_obese, is_ovwt, is_undwt, is_male, is_female, fam_decoded= 0,0,0,0,0,0,0

    if inp_sex ==0:
        is_female =1
    else:
        is_male=1

# Assigning financial status based on poverty threshold

    if  inp_poverty <= 2:
        inp_finstat = 0
    elif inp_poverty > 2 and inp_poverty < 4:
        inp_finstat = 1
    elif inp_poverty >= 4 and inp_poverty <= 5:
        inp_finstat = 2


# assigning values to healthy, underweight, overweight, obese based on BMi value
    if inp_bmi < 18.5:
        is_undwt =1
    elif inp_bmi >= 18.5 and inp_bmi < 25:
        is_healthy =1
    elif inp_bmi >= 25 and inp_bmi < 30:
        is_ovwt=1
    elif inp_bmi >=30:
        is_obese = 1


    if inp_fam ==1:
        fam_decoded =0
    elif int(inp_fam)>1 and int(inp_fam)<=4:
        fam_decoded =1
    else:
        fam_decoded =2

    inp_features = [inp_bmi,inp_age,inp_marital,inp_alc,inp_drg,inp_fam,inp_school,inp_diab,inp_poverty,is_female,is_male,inp_finstat,fam_decoded,is_healthy,is_obese,is_ovwt,is_undwt]
    # print(inp_features)

    pre_final_features = [np.array(inp_features)]
    prediction = model.predict(pre_final_features)   
    print('predictio value is ', prediction)

    if (prediction[0] == 1):
        output = "You are highly risky to suffer from depression"
    elif(prediction[0] == 0):
        output = "You are in a safe zone"
    else:
        output = "Not sure"

     # Get the coefficients of the logistic regression model
    fig= plt.figure(figsize=(5, 4)) # Set the figure size to 8x6 inches
    inp_features1=['BMI', 'Age', 'M-Status', 'Alcohol', 'Drugs', 'Family', 'Schooling', 'Diabetes', 'Poverty', 'Female', 'Male', 'F-Status', 'Family Size', 'Healthy BMI', 'Obese BMI', 'Overweight BMI', 'Underweight BMI']
    coefs = model.coef_[0]
    pos_coefs = coefs[coefs > 0]
    pos_xtics = [inp_features1[i] for i in range(len(inp_features)) if coefs[i] > 0]

    # Create a bar plot of the positive coefficients
    plt.bar(range(len(pos_coefs)), pos_coefs,color='green')
    plt.xticks(range(len(pos_xtics)), pos_xtics, rotation=45,fontsize=6)
    plt.xlabel('Input Feature')
    plt.ylabel('Coefficient')
    plt.title('Impact of Fields on Depression Prediction')
    fig.set_facecolor('aliceblue')

    # Save the plot to a file
    plot_filename = 'plot.png'
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    plt.savefig(os.path.join(static_path, 'plot.png'))

    return redirect(url_for('results', prediction_text=output, form_data=form_data, plot_filename=plot_filename))


@app.route('/results')
def results():
    disp_output = request.args.get('prediction_text')
    form_data_str = request.args.get('form_data')
    form_data = ast.literal_eval(form_data_str)
    plot_filename = request.args.get('plot_filename')
    # Create a dictionary of recommendations for each input value
    recommendations = {
        'isalc': ['Aim to reduce alcohol intake gradually', 'Try alcohol free days and find alternative ways to relax such as practicing mindfulness, taking up a new hobby, or spending time outdoors.'],
        'drugs': ['Drugs usage should be stopped immediately.', 'Get counseling from a mental health professional to solve the underlying issues.'],
        'poverty': ['Consult a financial advisor or try to get community help.', 'Try to find alternative sources of income such as taking up a part-time job or exploring online platforms to earn extra income.'],
        # Add more recommendations for other input values
    }
    print("in results",type(form_data))
    
    no_rec='You are healthy and maintain your lifestyle to stay healthy'
    input_recommendations = []
    for input_name, input_value in form_data.items():
        if input_name =='poverty':
            if float(input_value) < 4:
                input_recommendations += recommendations[input_name]
        if input_name in recommendations and input_value == '1':
            input_recommendations += recommendations[input_name]
    if len(input_recommendations)==0:
        input_recommendations.append(no_rec)
    print(input_recommendations)
    # Display the prediction result and input recommendations on the "results" HTML page
    return render_template('results.html', messages='{}'.format(disp_output), recommendations=input_recommendations,plot_filename=plot_filename)


if __name__=="__main__":
    app.run(debug=True)