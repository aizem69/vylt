from flask import Flask, render_template, request, redirect, session
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'vylt_secret_key_123'  #Secret key for session

# Home route
@app.route('/')
def home():
    return "VYLT SYSTEM ACTIVE - Welcome to the grind vault!"

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        age = request.form['umur']
        weight = float(request.form['weight'])
        height_cm = float(request.form['height'])
        goal = request.form['goal']

        # Kira BMI
        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2),2)

        # Check for duplicate name
        if os.path.exists('data/users.csv'):
            with open('data/users.csv', mode = 'r') as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if row[0] == name:
                   # if len(row) >= 2 and row[0] == name:
                        return "⚠️Name already exists. Please choose another one."
                    
        # Write new user data
        file_exists = os.path.exists('data/users.csv')
        with open('data/users.csv', mode ='a', newline='') as file:
            writer  = csv.writer(file)
            if not file_exists or os.path.getsize('data/users.csv') == 0:
                writer.writerow(['name', 'password', 'umur', 'weight', 
                                 'height', 'bmi', 'goal', ])
            writer.writerow([name, password, age, weight, height_cm, bmi, goal])

        session['name'] = name
        return redirect('/dashboard')
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already Logged in, redirect away
    if session.get('name'):
        return redirect('/dashboard') # or '/progress'
    
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        # Semak dalam users.csv
        with open('data/users.csv', mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 7 and row[0] == name and row[1] == password:
                    session['name'] = name
                    return redirect('/dashboard') #Redirect dashboard
                   
        return "Login failed. Please check your name and password."
        
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    name = session.get('name')
    if not name:
        return redirect('/login')
    
    with open('data/users.csv', mode ='r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) >= 7 and row[0] == name:
                weight = float (row[3])
                height_cm = float(row[4])
                bmi = round(weight / ((height_cm / 100) ** 2), 2)
                goal = row[6]
                meal_plan = get_meal_plan(goal)
                feedback = get_weight_feedback(name)
                progress_done = {}  # Initialize before reading weeklog.csv

                # BMI status
                if bmi < 18.5:
                    status = "Underweight"
                elif 18.6 <= bmi < 25:
                    status = "Normal"
                elif 25 <= bmi < 30:
                    status = "Overweight"
                else:
                    status = "Obese"

                # Workout plan
                if goal == "bulk":
                    plan = ["Mon: Upper Body Pump", "Tue: Rest", "Wed: Lower Body", 
                            "Thu: Cardio 20 min", "Fri: Full-body HIIT", 
                            "Sat: Rest", "Sun: Core Blaster"]
                elif goal == "cut":
                    plan = ["Mon: HIIT + Jump Rope", "Tue: Core Burnout", "Wed: Rest", 
                            "Thu: Full-body circuit", "Fri: Walk 5km", "Sat: Yoga/Stretch", 
                            "Sun: Rest"]
                else:
                    plan = ["Mon: Bodyweight Routine", "Tue: Rest", "Wed: Dumbbell Flow", 
                            "Thu: Jogging", "Fri: Rest", "Sat: Resistance Bands", 
                            "Sun: Optional Active Day"]
                    
                week_days = ["Mon", "Tue", "Wed", "Thu", "Fri","Sat","Sun"]
                progress_done = {}

                if os.path.exists('data/weeklog.csv'):
                    with open('data/weeklog.csv', mode ='r') as file:
                        reader = csv.reader(file)
                        next(reader, None)
                        for row in reader:
                            if len(row) >= 3 and row[0] == name:
                                progress_done[row[1]] = row[2]

                # If some days not found, default to 'no'
                for day in week_days:
                    if day not in progress_done:
                        progress_done[day] = 'no'

                progress_percentage, motivation = get_weekly_progress(name)   
     

                return render_template('dashboard.html', 
                                       name=name, 
                                       bmi=bmi, 
                                       status_bmi=status,
                                       goal=goal.capitalize(), 
                                       plan=plan, 
                                       feedback=feedback,
                                       meal_plan=meal_plan,
                                       progress_done=progress_done,
                                       progress_percentage=progress_percentage,
                                       motivation=motivation
                                       )
            
        return "User not found."



# Progress route
@app.route('/progress', methods=['GET', 'POST'])
def progress():
    name = session.get('name')
    if not name:
        return redirect('/login')

    if request.method == 'POST':
        weight = request.form['weight']
        today  = datetime.today().strftime('%Y-%m-%d')

        file_exists = os.path.isfile('data/progress.csv')
        with open('data/progress.csv', mode='a',newline='') as file:
            writer = csv.writer(file)
            if not file_exists or os.path.getsize('data/progress.csv') == 0:
                writer.writerow(['name', 'date', 'weight'])
            writer.writerow([name, today, weight])

        generate_chart(name) # Update graph after new entry

        height_cm = None
        users = []

        with open('data/users.csv', mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if len(row) < 7:
                    users.append(row)
                    continue
                if row[0] == name:
                    height_cm = float(row[4])
                    new_bmi = round(float(weight) / ((height_cm / 100) ** 2), 2)
                    row[3] = str(weight) # Update weight
                    row[5] = str(new_bmi) # Update BMI
                users.append(row)

        with open('data/users.csv', mode ='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(users)
         
    logs = [] 
    try:
        with open('data/progress.csv', mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 3 and row[0] == name:
                    logs.append(row)
                    

    except FileNotFoundError:
        pass
        
    return render_template('progress.html', name=name, logs=logs)


def generate_chart(name):
    dates = []
    weights = []

    with open('data/progress.csv', mode ='r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) >= 3 and row[0] == name:
                dates.append(row[1])
                weights.append(float(row[2]))

    if not dates or not weights:
        return # No data to plot
    
    plt.figure(figsize=(6,4))
    plt.plot(dates, weights, marker='o')
    plt.title(f'Weight Progress for {name}')
    plt.xlabel('Date')
    plt.ylabel('Weight (kg)')
    plt.grid(True)
    plt.tight_layout()
    
    # Save to static folder
    if not os.path.exists('static'):
        os.makedirs('static')
    plt.savefig('static/progress_chart.png')
    plt.close

def get_weight_feedback(name):
    weights = []

    with open('data/progress.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) >= 3 and row[0] ==name:
                weights.append(float(row[2]))

    if len(weights) < 2:
        return "Log more entries to track progress."
    
    latest = weights[-1]
    previous = weights[-2]
    diff = round(latest - previous, 1)

    if diff > 0:
        return f"🔥 Great! You've gained +{diff}kg since last entry. Keep building!"
    elif diff < 0:
        return f"⚠️ You’ve dropped {abs(diff)}kg. Don’t worry — stay consistent!"
    else:
        return "➖ No change. Let’s push harder this week!"
    

def get_meal_plan(goal):
    if goal == "bulk":
        return [
            "🍳 Breakfast: 4 eggs, oats with peanut butter, banana",
            "🥩 Lunch: Chicken breast, brown rice, broccoli",
            "🥤 Snack: Protein shake, almonds",
            "🍝 Dinner: Pasta with minced beef, spinach",
            "🌙 Supper: Greek yogurt, 1 tbsp honey"
        ]
    elif goal == "cut":
        return [
            "🍳 Breakfast: 2 boiled eggs, cucumber slices",
            "🥗 Lunch: Grilled fish, mixed greens, lemon dressing",
            "🍵 Snack: Green tea, 10 almonds",
            "🍛 Dinner: Tofu stir-fry, cauliflower rice",
            "🌙 Supper: Protein shake with water"
        ]
    else:  # fit
        return [
            "🍞 Breakfast: Wholegrain toast, 2 eggs, fruit",
            "🥙 Lunch: Chicken wrap with salad",
            "🍌 Snack: Banana, nuts",
            "🥘 Dinner: Grilled salmon, quinoa, veggies",
            "🧉 Supper: Herbal tea"
        ]

# Weekly Progress

def get_weekly_progress(name):
    total_days = 7
    completed = 0

    if os.path.exists('data/weeklog.csv'):
        with open('data/weeklog.csv', mode ='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 3 and row[0] == name and row[2] == 'yes':
                    completed += 1

    progress_percentage = round((completed / total_days) * 100)

    # Motivation message based on performance
    if progress_percentage == 0:
        message = "😴 Let's wake up and crush it this week!"
    elif progress_percentage < 30:
        message = "🚶‍♂️ Just getting started. Keep pushing!"
    elif progress_percentage < 60:
        message = "💥 Nice pace! You're halfway to the top!"
    elif progress_percentage < 90:
        message = "🔥 Grinding strong! Almost there!"
    else:
        message = "🏆 MONSTER MODE ACTIVATED! You're unstoppable!"
          
    return progress_percentage, message

# Update Week
@app.route('/update_week', methods=['POST'])
def update_week():
    name = session.get('name')
    if not name:
        return redirect('/login')
    
    checked = request.form.getlist('done_days')
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    with open('data/weeklog.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'day', 'done'])
        for day in week_days:
            status = 'yes' if day in checked else 'no'
            writer.writerow([name, day, status])

    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('name', None) # Clear session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)