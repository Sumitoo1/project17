import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Dataset for the Car Recommendation System with local image paths
data = {
    "Car Model": ["Maruti Alto K10", "Maruti S-Presso", "Renault Kwid", "Maruti Ignis", "Maruti Eeco",
                  "Renault Kiger", "Maruti Celerio", "Citroen C3", "Renault Triber", "Maruti Brezza"],
    "Price": ["Rs. 3.99 - 5.96 Lakh", "Rs. 4.26 - 6.11 Lakh", "Rs. 4.70 - 6.45 Lakh", "Rs. 5.84 - 8.30 Lakh",
              "Rs. 5.32 - 6.58 Lakh", "Rs. 6.00 - 11.23 Lakh", "Rs. 5.36 - 7.10 Lakh", "Rs. 6.16 - 9.08 Lakh",
              "Rs. 6.00 - 8.98 Lakh", "Rs. 8.34 - 14.14 Lakh"],
    "Mileage": ["24.39 to 33.85 kmpl", "24.44 to 32.73 kmpl", "21.7 to 22 kmpl", "20.89 kmpl", "20.89 kmpl",
                "20.89 kmpl", "20.89 kmpl", "19.3 kmpl", "18.2 to 19 kmpl", "19.05 to 25.51 kmpl"],
    "Engine": ["998 cc", "998 cc", "999 cc", "1197 cc", "1197 cc", "1197 cc", "1197 cc", "1198 to 1199 cc",
               "999 cc", "1462 cc"],
    "Safety Rating": ["2 Star (Global NCAP)", "0 Star (Global NCAP)", "1 Star (Global NCAP)", "1 Star (Global NCAP)",
                      "1 Star (Global NCAP)", "1 Star (Global NCAP)", "1 Star (Global NCAP)", "1 Star (Global NCAP)",
                      "4 Star (Global NCAP)", "4 Star (Global NCAP)"],
    "Fuel Type": ["Petrol & CNG", "Petrol & CNG", "Petrol", "Petrol", "Petrol & CNG", "Petrol & CNG", "Petrol & CNG",
                  "Petrol", "Petrol", "Petrol & CNG"],
    "Transmission": ["Manual & Automatic", "Manual & Automatic", "Manual & Automatic", "Manual & Automatic",
                     "Manual", "Manual", "Manual", "Manual", "Manual & Automatic", "Manual & Automatic"],
    "Seating Capacity": ["5 Seater", "4 & 5 Seater", "5 Seater", "5 Seater", "5 & 7 Seater", "5 & 7 Seater",
                         "5 & 7 Seater", "5 Seater", "7 Seater", "5 Seater"]
}

# Convert to DataFrame
@st.cache_data
def load_and_clean_data():
    car_df = pd.DataFrame(data)

    # Data Cleaning
    car_df['Price'] = car_df['Price'].str.replace("Rs. ", "").str.replace(" Lakh", "")
    car_df[['Min_Price', 'Max_Price']] = car_df['Price'].str.split(' - ', expand=True)
    car_df['Min_Price'] = pd.to_numeric(car_df['Min_Price'], errors='coerce') * 100000
    car_df['Min_Price_Lakh'] = car_df['Min_Price'] / 100000

    # Clean Mileage column
    def clean_mileage(mileage):
        if 'to' in mileage:
            min_mileage, max_mileage = mileage.split(' to ')
            return (float(min_mileage.split(' ')[0]), float(max_mileage.split(' ')[0]))
        else:
            return float(mileage.split(' ')[0]), float(mileage.split(' ')[0])

    car_df[['Min_Mileage', 'Max_Mileage']] = car_df['Mileage'].apply(clean_mileage).apply(pd.Series)

    # Clean Safety Rating
    car_df['Safety Rating'] = car_df['Safety Rating'].apply(lambda x: int(x.split()[0]) if x.split()[0].isdigit() else 0)

    # Clean Seating Capacity
    car_df['Seating Capacity'] = car_df['Seating Capacity'].apply(
        lambda x: max([int(i.split()[0]) for i in x.split('&')]))

    return car_df

car_df = load_and_clean_data()

# Streamlit App
st.title("🚗 Car Recommendation System")
st.write("### Enter your budget to find the best cars for you!")

# Filters for Fuel Type and Transmission
fuel_type_filter = st.selectbox("Select preferred Fuel Type", options=["Any", "Petrol", "Petrol & CNG"])
transmission_filter = st.selectbox("Select preferred Transmission", options=["Any", "Manual", "Automatic"])

# Budget input
budget = st.number_input("🔹 Enter your car budget (greater than ₹3,00,000):",
                         min_value=300000, step=50000, value=None, key="budget_input")

if budget is not None:
    if budget <= 300000:
        st.write("### ❌ Your budget is below ₹3,00,000. We do not have any cars in this price range.")
    elif budget >= 2000000:
        st.write("### ❌ Your car is too expensive, we do not have it in our database.")
    else:
        rounded_budget = round(budget / 100000) * 100000
        filtered_cars = car_df[car_df['Min_Price'] <= rounded_budget]

        if not filtered_cars.empty:
            st.write(f"### ✅ Cars available within your budget of ₹{rounded_budget / 100000} Lakh:")

            for _, row in filtered_cars.iterrows():
                st.markdown(f"### 🚗 {row['Car Model']}")
                st.write(f"Price: ₹{row['Min_Price_Lakh']:.2f} Lakh")
                st.write(f"Mileage: {row['Min_Mileage']} to {row['Max_Mileage']} kmpl")
                st.write(f"Engine: {row['Engine']} cc")
                st.write(f"Fuel Type: {row['Fuel Type']}")
                st.write(f"Transmission: {row['Transmission']}")
                st.write(f"Seating Capacity: {row['Seating Capacity']} Seater")
                st.write(f"Safety Rating: {row['Safety Rating']} ⭐")

            # Feature Comparison Graphs
            st.write("### 📊 Car Feature Comparison")
            fig, axs = plt.subplots(2, 2, figsize=(14, 10))

            axs[0, 0].bar(filtered_cars['Car Model'], filtered_cars['Min_Price_Lakh'], color='skyblue', width=0.5)
            axs[0, 0].set_title('💰 Price Comparison')
            axs[0, 0].set_ylabel('Price (Lakh)')
            axs[0, 0].tick_params(axis='x', rotation=45)

            axs[0, 1].bar(filtered_cars['Car Model'], filtered_cars['Min_Mileage'], color='lightgreen', width=0.5)
            axs[0, 1].set_title('⛽ Mileage Comparison')
            axs[0, 1].set_ylabel('Mileage (kmpl)')
            axs[0, 1].tick_params(axis='x', rotation=45)

            axs[1, 0].bar(filtered_cars['Car Model'], filtered_cars['Seating Capacity'], color='gold', width=0.5)
            axs[1, 0].set_title('🪑 Seating Capacity')
            axs[1, 0].set_ylabel('Seats')
            axs[1, 0].tick_params(axis='x', rotation=45)

            axs[1, 1].bar(filtered_cars['Car Model'], filtered_cars['Safety Rating'], color='lightcoral', width=0.5)
            axs[1, 1].set_title('🛡️ Safety Rating')
            axs[1, 1].set_ylabel('Stars')
            axs[1, 1].set_ylim(0, 5)
            axs[1, 1].tick_params(axis='x', rotation=45)

            plt.tight_layout()
            st.pyplot(fig)

        else:
            st.write("❌ No cars available in your selected budget and filters.")
