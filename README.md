# PCCOE Attendance Tracker

This Streamlit web application helps PCCOE (Pimpri Chinchwad College of Engineering) students monitor their attendance across all subjects. It provides insights like:

- Overall attendance percentage
- Subject-wise attendance breakdown
- How many classes you can miss while maintaining 75%
- How many classes you need to attend to reach 75%

## Features

- **User-friendly Interface:** Easy-to-use Streamlit web application.
- **Secure Login:** Uses your PCET ERP credentials to fetch attendance data (credentials are not stored).
- **Comprehensive Attendance Overview:** Displays overall and subject-wise attendance percentages.
- **Bunk Limit Calculation:** Calculates the number of classes you can miss while maintaining the minimum 75% attendance.
- **Attendance Required Calculation:** Calculates the number of classes you need to attend to reach the minimum 75% attendance.
- **Visualizations:** Generates bar charts and pie charts for easy understanding of attendance data.
- **Data Export:** Allows users to download attendance data in CSV format.
- **Risk Analysis:** Highlights subjects with low attendance and provides recommendations.
- **Responsive Design:** Works well on various screen sizes.

## Screenshots
![Image](https://github.com/user-attachments/assets/47a8394a-9781-4a06-8498-daf96610f6f1)
![Image](https://github.com/user-attachments/assets/75d1d340-0f94-496d-b815-160245ddb6b9)
![Image](https://github.com/user-attachments/assets/ba503d15-2e02-41a3-afc7-601a68397d75)
![Image](https://github.com/user-attachments/assets/fa783f0e-a2eb-4188-831c-68e1a3c042f3)
![Image](https://github.com/user-attachments/assets/8e1f66be-2177-4f3c-b17d-779a97cb1f4b)


## Installation

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/yourusername/pccoe-attendance-tracker.git](https://www.google.com/search?q=https://github.com/yourusername/pccoe-attendance-tracker.git)
   cd pccoe-attendance-tracker
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS and Linux
   venv\Scripts\activate  # On Windows
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit application:**

   ```bash
   streamlit run app.py
   ```

   Replace `app.py` with the actual name of your Streamlit script.

## Usage

1. Open the Streamlit application in your web browser.
2. Enter your PCET ERP username and password.
3. Click the "Fetch Attendance" button.
4. View your attendance analytics, including overall attendance, subject-wise attendance, and visualizations.
5. Download attendance data as a CSV file if needed.

## Dependencies

- `streamlit`
- `selenium`
- `webdriver_manager`
- `matplotlib`
- `pandas`
- `re`
- `time`

## Contributing

Contributions are welcome! If you have any suggestions or bug reports, please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Create a new Pull Request.

## Author

- Vedant Kale

## Disclaimer

This tool is not officially affiliated with PCCOE. It is designed to help students track their attendance. Use it responsibly and at your own discretion.

