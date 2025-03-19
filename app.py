from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import matplotlib.pyplot as plt
import io
import base64
import streamlit as st
import pandas as pd
import datetime

# Set page configuration
st.set_page_config(
    page_title="PCCOE Attendance Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4527A0;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #5E35B1;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 1rem;
        color: #6c757d;
    }
    .warning {
        color: #f44336;
        font-weight: bold;
    }
    .success {
        color: #4CAF50;
        font-weight: bold;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.8rem;
        color: #6c757d;
    }
    .sidebar-content {
        padding: 1.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

def fetch_attendance(username, password):
    with st.spinner('Fetching your attendance data...'):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://learner.pceterp.in/")
            time.sleep(1)

            driver.find_element(By.XPATH, "//input[@type='text']").send_keys(username)
            driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
            driver.find_element(By.XPATH, "//button[contains(@class, 'v-btn') and contains(., 'Sign In')]").click()
            time.sleep(2)

            driver.get("https://learner.pceterp.in/attendance")
            time.sleep(2)

            try:
                student_name_element = driver.find_element(By.XPATH, "//span[contains(@class, 'ml-3 font-weight-bold text-medium-emphasis')]")
                student_name = student_name_element.text.strip()
            except:
                student_name = "Unknown"

            subject_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'v-col-sm-4')]")

            attendance_records = []
            total_attended = 0
            total_lectures = 0

            for block in subject_blocks:
                try:
                    subject_name = block.find_element(By.XPATH, ".//div[@class='pb-5']").text.split("\n")[-1]
                    attendance_text = block.find_element(By.XPATH, ".//span[contains(text(), '/')]").text.strip()
                    percentage = block.find_element(By.XPATH, ".//div[@class='v-progress-circular__content']").text.strip()

                    try:
                        attendance_type = block.find_element(By.XPATH, ".//div[@class='v-chip__content']").text.strip().split()[0]
                    except:
                        attendance_type = "Unknown"

                    match = re.search(r'(\d+) / (\d+)', attendance_text)
                    if match:
                        attended, total = map(int, match.groups())
                    else:
                        attended, total = 0, 0

                    if total == 0:
                        continue

                    total_attended += attended
                    total_lectures += total

                    attendance_records.append({
                        "Subject": subject_name,
                        "Attended": attended,
                        "Total": total,
                        "Attendance": attendance_text,
                        "Percentage": float(percentage.replace("%", "")),
                        "Type": attendance_type
                    })
                except:
                    pass

            driver.quit()

            attendance_records.sort(key=lambda x: x["Percentage"])

            current_percentage = (total_attended / total_lectures) * 100 if total_lectures > 0 else 0
            lectures_to_bunk = calculate_bunk_limit(total_attended, total_lectures) if current_percentage >= 75 else 0
            lectures_to_attend = calculate_lectures_to_attend(total_attended, total_lectures) if current_percentage < 75 else 0

            return student_name, current_percentage, attendance_records, lectures_to_bunk, lectures_to_attend, total_attended, total_lectures
        except Exception as e:
            driver.quit()
            st.error(f"An error occurred: {str(e)}")
            return None, 0, [], 0, 0, 0, 0


def calculate_bunk_limit(attended, total):
    lectures_to_bunk = 0
    while ((attended / (total + lectures_to_bunk)) * 100) >= 75:
        lectures_to_bunk += 1
    return lectures_to_bunk - 1


def calculate_lectures_to_attend(attended, total):
    """Calculate how many consecutive lectures need to be attended to reach 75%"""
    additional_lectures = 0
    while ((attended + additional_lectures) / (total + additional_lectures)) * 100 < 75:
        additional_lectures += 1
    return additional_lectures


def generate_chart(subjects, title, colors):
    if not subjects:
        return None

    plt.figure(figsize=(10, 6))
    subjects_names = [sub["Subject"] for sub in subjects]
    percentages = [sub["Percentage"] for sub in subjects]

    bars = plt.bar(subjects_names, percentages, color=colors)
    
    # Add data labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Add a horizontal line at 75%
    plt.axhline(y=75, color='r', linestyle='--', alpha=0.7, label='Minimum Required (75%)')
    
    plt.xlabel("Subjects", fontweight='bold')
    plt.ylabel("Attendance (%)", fontweight='bold')
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.ylim(0, 105)  # Give some space for data labels
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', dpi=100)
    img_io.seek(0)
    return base64.b64encode(img_io.read()).decode("utf-8")


def generate_pie_chart(attended, total):
    plt.figure(figsize=(8, 6))
    labels = ['Attended', 'Missed']
    sizes = [attended, total - attended]
    colors = ['#4CAF50', '#f44336']
    explode = (0.1, 0)  # explode the first slice
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Overall Attendance Distribution', fontsize=14, fontweight='bold', pad=20)
    
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', dpi=100)
    img_io.seek(0)
    return base64.b64encode(img_io.read()).decode("utf-8")


# Sidebar content
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    st.markdown("### PCCOE Attendance Tracker")
    st.markdown("---")
    
    st.markdown("""
    **About this app:**
    
    This tool helps PCET students monitor their attendance across all subjects. It provides insights like:
    
    - Overall attendance percentage
    - Subject-wise attendance breakdown
    - How many classes you can miss while maintaining 75%
    - How many classes you need to attend to reach 75%
    
    **How to use:**
    1. Enter your PCET ERP credentials
    2. Click 'Fetch Attendance'
    3. View your attendance analytics
    
    **Privacy Note:**
    Your credentials are not stored and are only used to fetch your attendance data.
    """)
    
    st.markdown("---")
    
    st.markdown("""**Developed By Vedant Kale ❤️**""")
    
    st.markdown("</div>", unsafe_allow_html=True)


# Main content
st.markdown('<h1 class="main-header">📊 PCCOE Attendance Tracker</h1>', unsafe_allow_html=True)

# Create two columns for login
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Fetch Attendance", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if login_button:
    if username and password:
        student_name, current_percentage, attendance_data, lectures_to_bunk, lectures_to_attend, total_attended, total_lectures = fetch_attendance(username, password)

        if attendance_data:
            # Student information header
            st.markdown(f'<h2 class="sub-header">Student: {student_name}</h2>', unsafe_allow_html=True)
            
            # Summary stats in cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'''
                <div class="stat-card">
                    <div class="stat-value">{'%.2f' % current_percentage}%</div>
                    <div class="stat-label">Overall Attendance</div>
                    <div class="{'success' if current_percentage >= 75 else 'warning'}">
                        {'✅ Above minimum' if current_percentage >= 75 else '⚠️ Below minimum'}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
            with col2:
                st.markdown(f'''
                <div class="stat-card">
                    <div class="stat-value">{total_attended}/{total_lectures}</div>
                    <div class="stat-label">Classes Attended</div>
                    <div>Out of total lectures</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                if lectures_to_bunk > 0:
                    st.markdown(f'''
                    <div class="stat-card">
                        <div class="stat-value">{lectures_to_bunk}</div>
                        <div class="stat-label">Classes you can miss</div>
                        <div class="success">While maintaining 75%</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="stat-card">
                        <div class="stat-value">{lectures_to_attend}</div>
                        <div class="stat-label">Classes to attend</div>
                        <div class="warning">To reach 75% minimum</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            with col4:
                st.markdown(f'''
                <div class="stat-card">
                    <div class="stat-value">{len(attendance_data)}</div>
                    <div class="stat-label">Total Subjects</div>
                    <div>With attendance tracking</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Create tabs for different sections
            tab1, tab2, tab3 = st.tabs(["📊 Attendance Details", "📉 Charts & Visualization", "🔍 Analysis"])
            
            with tab1:
                # Display the attendance records as a table with styling
                st.markdown('<h3 class="sub-header">Subject-wise Attendance Records</h3>', unsafe_allow_html=True)
                
                # Custom styling for the DataFrame
                def color_percentage(val):
                    color = 'red' if val < 75 else 'green'
                    return f'background-color: {color}; color: white'
                
                df = pd.DataFrame(attendance_data)
                
                # Apply styling to the percentage column
                styled_df = df.style.applymap(
                    lambda x: color_percentage(x) if x < 75 else 'background-color: green; color: white', 
                    subset=['Percentage']
                )
                
                # Add a 'Risk Level' column
                df['Risk Level'] = df['Percentage'].apply(
                    lambda x: '⚠️ High Risk' if x < 65 else 
                                ('⚠️ Medium Risk' if x < 75 else 
                                '✅ Safe')
                )
                
                # Display the styled DataFrame
                st.dataframe(
                    df[['Subject', 'Attended', 'Total', 'Percentage', 'Risk Level']],
                    column_config={
                        'Subject': 'Subject Name',
                        'Percentage': st.column_config.ProgressColumn(
                            'Attendance %',
                            format='%.1f%%',
                            min_value=0,
                            max_value=100,
                        ),
                        'Risk Level': 'Status'
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button for attendance data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Attendance Data",
                    data=csv,
                    file_name=f"attendance_{student_name}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
            
            with tab2:
                st.markdown('<h3 class="sub-header">Attendance Visualizations</h3>', unsafe_allow_html=True)
                
                # Generate charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Overall attendance pie chart
                    pie_chart = generate_pie_chart(total_attended, total_lectures)
                    if pie_chart:
                        st.image(f"data:image/png;base64,{pie_chart}", caption="Overall Attendance Distribution")
                
                with col2:
                    # Subject with lowest attendance
                    subjects_below = [s for s in attendance_data if s["Percentage"] < 75]
                    if subjects_below:
                        st.markdown(f"### Subjects Below 75% ({len(subjects_below)})")
                        for subject in subjects_below:
                            st.markdown(f"""
                            <div style="padding: 10px; margin-bottom: 5px; background-color: rgba(255, 0, 0, 0.1); border-left: 5px solid red; border-radius: 5px;">
                                <b>{subject['Subject']}</b>: {subject['Percentage']:.1f}% ({subject['Attendance']})
                            </div>
                            """, unsafe_allow_html=True)
                
                # Bar charts
                st.markdown("### Attendance by Subject")
                chart_type = st.radio("Choose visualization", ["All Subjects", "Lowest Attendance", "Highest Attendance"])
                
                if chart_type == "All Subjects":
                    all_colors = ['green' if s["Percentage"] >= 75 else 'red' for s in attendance_data]
                    all_chart = generate_chart(attendance_data, "Attendance Percentage for All Subjects", all_colors)
                    if all_chart:
                        st.image(f"data:image/png;base64,{all_chart}")
                
                elif chart_type == "Lowest Attendance":
                    low_attendance = attendance_data[:6]  # 6 lowest
                    low_colors = ["red"] * 6
                    low_chart = generate_chart(low_attendance, "Top 6 Lowest Attendance Subjects", low_colors)
                    if low_chart:
                        st.image(f"data:image/png;base64,{low_chart}")
                
                else:  # Highest Attendance
                    high_attendance = attendance_data[-6:]  # 6 highest
                    high_colors = ["green"] * 6
                    high_chart = generate_chart(high_attendance, "Top 6 Highest Attendance Subjects", high_colors)
                    if high_chart:
                        st.image(f"data:image/png;base64,{high_chart}")
            
            with tab3:
                st.markdown('<h3 class="sub-header">Attendance Analysis & Recommendations</h3>', unsafe_allow_html=True)
                
                # Analysis and recommendations
                if current_percentage < 75:
                    st.warning(f"⚠️ Your current attendance ({current_percentage:.2f}%) is below the required 75%. You need to attend at least {lectures_to_attend} more consecutive classes to reach the minimum requirement.")
                    
                    # Specific recommendations for subjects
                    critical_subjects = [s for s in attendance_data if s["Percentage"] < 65]
                    if critical_subjects:
                        st.error("#### Critical Subjects")
                        st.markdown("These subjects require immediate attention:")
                        for subject in critical_subjects:
                            classes_needed = int((0.75 * subject["Total"] - subject["Attended"]) / 0.25) + 1
                            st.markdown(f"""
                            <div style="padding: 10px; margin-bottom: 5px; background-color: rgba(255, 0, 0, 0.1); border-left: 5px solid red; border-radius: 5px;">
                                <b>{subject['Subject']}</b>: Currently at {subject['Percentage']:.1f}%<br>
                                You need to attend approximately {classes_needed} more consecutive classes for this subject to reach 75%
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.success(f"✅ Your overall attendance ({current_percentage:.2f}%) is above the required 75%. You can miss up to {lectures_to_bunk} classes while maintaining the minimum requirement.")
                    
                    # Show which subjects have room for absence
                    safe_subjects = sorted([s for s in attendance_data if s["Percentage"] > 80], key=lambda x: x["Percentage"], reverse=True)
                    if safe_subjects:
                        st.markdown("#### Subjects with Safe Attendance")
                        st.markdown("These subjects have sufficient attendance:")
                        for subject in safe_subjects[:5]:  # Show top 5 safe subjects
                            classes_can_miss = int((subject["Percentage"] - 75) * subject["Total"] / 75)
                            st.markdown(f"""
                            <div style="padding: 10px; margin-bottom: 5px; background-color: rgba(0, 255, 0, 0.1); border-left: 5px solid green; border-radius: 5px;">
                                <b>{subject['Subject']}</b>: Currently at {subject['Percentage']:.1f}%<br>
                                You can miss approximately {classes_can_miss} more classes for this subject while maintaining 75%
                            </div>
                            """, unsafe_allow_html=True)
                
                # General attendance tips
                st.markdown("#### General Tips for Maintaining Attendance")
                st.markdown("""
                - Prioritize attending classes for subjects with lower attendance percentages
                - Set reminders for classes to avoid missing them
                - If you must miss a class, try to choose from subjects with higher attendance percentages
                - Keep track of your attendance regularly using this tool
                - Remember that medical absences might be considered with proper documentation
                """)

        else:
            st.error("Failed to fetch attendance. Check your credentials and try again.")
    else:
        st.warning("Please enter username and password.")

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 PCCOE Attendance Tracker | This tool is not officially affiliated with PCCOE. It is designed to help students track their attendance.</p>
</div>
""", unsafe_allow_html=True)