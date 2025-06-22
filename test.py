# def calculate_bmi(weight, height_cm):
#     height_m = height_cm /100
#     bmi = round(weight / height_m ** 2, 2)
#     return bmi


# def get_bmi_status(bmi):
#     if bmi < 18.5:
#         return "Underweight"
#     elif bmi < 25:
#         return "Normal"
#     elif bmi < 30:
#         return "Overweight"
#     else:
#         return "Obese"
    
# # Generate Feedback

# def generate_feedback(bmi, goal):
#     if goal == "Fit" and 18.5 <= bmi <= 24.9:
#         return "You're right on track. Keep it up!"
#     elif goal == "Bulk" and bmi < 24:
#         return "Time to eat more and lift heavy!"
#     elif goal == "Cut" and bmi > 24:
#         return "Let's shred and burn that fat!"
#     else:
#         return "Stay consistent with your plan"
    
# def show_user_summary(name, weight, height_cm, goal):
#     name = input("Enter your name: ")
#     weight = float(input("Enter your weight (kg): "))
#     height_cm = float(input("Enter your height (cm): "))
#     goal = input("Enter your fitness goal (Fit/Bulk/Cut): ")


#     bmi = calculate_bmi(weight, height_cm)
#     status = get_bmi_status(bmi)
#     feedback = generate_feedback(bmi, goal)

#     print(f"Name: {name}")
#     print(f"BMI: {bmi} ({status})")
#     print(f"Goal: {goal}")
#     print(f"Feedback: {feedback}")

# show_user_summary("Jimi", 68, 170, "Bulk")



days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
weekly_plan = ["Pull", "Push", "Dumbbell", "Lift", "Core", "Rest", "Holiday"]

for day, workout in zip(days, weekly_plan):
    print(f"{day}: {workout}")