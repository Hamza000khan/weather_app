import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] =True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)
# keky = '4e0f56738daaa9a28cf6ed4ba31b6f05'

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&appid=4e0f56738daaa9a28cf6ed4ba31b6f05'
    r = requests.get(url).json()
    return r


@app.route('/')
def index_get():
    cities = City.query.all()


    weather_data = []

    for city in cities:
        
        r = get_weather_data(city.name)
        # print(r)

        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon']
        }
        
        weather_data.append(weather)
    return render_template('weather.html', weather_data=weather_data)




@app.route('/', methods=['POST'])
def index():
    err_msg = ''
    new_city = request.form.get('city')

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'city does not exist in the world!'
        else:
            err_msg = 'city already exists in the database!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added succesfully!') 
    return redirect(url_for('index_get'))

@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }', 'success')
    return redirect(url_for('index_get'))

if __name__== '__main__':
    app.run()


# {'coord': {'lon': 77.22, 'lat': 28.67}, 'weather': [{'id': 721, 'main': 'Haze', 'description': 'haze', 'icon': '50n'}], 
# 'base': 'stations', 'main': {'temp': 290.93, 'feels_like': 288.88, 'temp_min': 290.15, 'temp_max': 292.04, 'pressure': 1021, 'humidity': 51},
#  'visibility': 2000, 'wind': {'speed': 2.1, 'deg': 300}, 'clouds': {'all': 0}, 'dt': 1581171967, 'sys': {'type': 1, 'id': 9165, 'country': 'IN', 'sunrise': 1581125734, 'sunset': 1581165301}, 
# 'timezone': 19800, 'id': 1273294, 'name': 'Delhi', 'cod': 200}