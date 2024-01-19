from flask import Flask,request,render_template
from flask_mysqldb import MySQL
import yaml
import numpy as np
import pickle
import pandas as pd

# importing model
model = pickle.load(open('model.pkl','rb'))
model_fertilizer = pickle.load(open('modelfertilizer_etc.pkl','rb'))  #for fertilizer prediction

# creating flask app
app = Flask(__name__)

#configuring the db
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("index.html")

#fetching data from the page and predicting the crop
@app.route("/predict",methods=['POST'])
def predict():
    name = request.form['name']
    N = request.form['Nitrogen']
    P = request.form['Phosporus']
    K = request.form['Potassium']
    temp = request.form['Temperature']
    humidity = request.form['Humidity']
    ph = request.form['Ph']
    rainfall = request.form['Rainfall']
    soil_color = request.form['Soil_color']
    
    #pushing the data into database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO CROP(nitrogen, phosphor, potassium, temperature, humidity, ph, rainfall, soil_color, name, date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())", (N, P, K, temp, humidity, ph, rainfall, soil_color, name))
    mysql.connection.commit()
    cur.close()

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    feature_list_fertilizer = [ soil_color,N, P, K,ph, rainfall,temp]
    single_pred = np.array(feature_list).reshape(1, -1)
    single_pred_fertilzer = np.array(feature_list_fertilizer).reshape(1, -1)
    
    prediction = model.predict(single_pred)
    prediction_fertilizer = model_fertilizer.predict(single_pred_fertilzer)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}
    
    fertilizer_dict = {0: 'Ferrous Sulphate', 1: 'Ammonium Sulphate', 2: 'SSP', 3: 'MOP', 4: 'DAP', 5: 'Sulphur', 
             6: 'Urea', 7: '10:10:10 NPK', 8: 'Hydrated Lime', 9: '10:26:26 NPK', 10: '50:26:26 NPK', 11: '18:46:00 NPK', 
             12: '19:19:19 NPK', 13: '12:32:16 NPK', 14: 'Magnesium Sulphate', 15: 'White Potash', 
             16: 'Chilated Micronutrient', 17: '13:32:26 NPK', 18: '20:20:20 NPK'
            }

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = f"{crop} is the best crop to be cultivated right there"
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."

    if prediction_fertilizer[0] in fertilizer_dict:
        fertilizer = fertilizer_dict[prediction_fertilizer[0]]
        result_1 = f"{fertilizer} is the best fertilizer to be used right there"
    else:
        result_1 = "Sorry, we could not determine the best fertilizer to be used with the provided data."
    return render_template('index.html',result = result, result_1 = result_1)




# python main
if __name__ == "__main__":
    app.run(debug=True)