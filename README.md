🚌 Real-Time Bus Arrival Prediction Using LSTM with Traffic and Weather Integration
📖 Overview

This project was developed as part of the Machine Learning Internship at PESU Rapid Research Center, PES University (June 2025 – July 2025).
The goal was to design a real-time bus ETA (Estimated Time of Arrival) prediction system that integrates live GPS data, traffic conditions, and weather context to enhance prediction accuracy.

The system employs a Long Short-Term Memory (LSTM) deep learning model, known for its strength in handling temporal dependencies and time-series data, and delivers real-time ETA updates through an interactive Streamlit web dashboard.

🧠 Key Contributions

🔹 Developed an LSTM-based model to predict bus arrival times using sequential GPS data and contextual features.

🔹 Integrated live traffic and weather data via APIs for real-time prediction refinement.

🔹 Built a complete machine learning pipeline — including preprocessing, feature engineering, model training, and evaluation.

🔹 Deployed the system on Streamlit, enabling users to visualize ETA predictions in real time.

🔹 Co-authored a research paper submitted to an international AI conference, presenting system design, methodology, and performance analysis.

⚙️ Tools & Technologies

Programming Language: Python

Frameworks/Libraries: TensorFlow, Keras, Pandas, NumPy, Scikit-learn

Web Framework: Streamlit

Visualization: Matplotlib, Plotly

APIs: Google Maps API (Traffic), OpenWeatherMap API (Weather)

Development Environment: Jupyter Notebook / VS Code

🏗️ System Architecture
+-------------------------------------------------------+
|                 Real-Time Data Sources                |
|  (GPS Feeds)   (Traffic API)   (Weather API)          |
+-------------------------------------------------------+
            ↓               ↓               ↓
+-------------------------------------------------------+
|           Data Preprocessing & Feature Engineering     |
|  - Timestamp alignment                                 |
|  - Speed & delay feature extraction                    |
|  - Context merging (traffic + weather)                 |
+-------------------------------------------------------+
            ↓
+-------------------------------------------------------+
|              LSTM-Based ETA Prediction Model           |
|  - Sequence input (past GPS positions & times)         |
|  - Contextual inputs (traffic, weather)                |
|  - Output: Predicted ETA (minutes)                     |
+-------------------------------------------------------+
            ↓
+-------------------------------------------------------+
|                  Streamlit Web Dashboard               |
|  - Interactive ETA visualization                       |
|  - Real-time bus tracking                              |
|  - Weather & traffic overlays                          |
+-------------------------------------------------------+

🧩 Model Summary

Architecture: LSTM layers with dropout regularization

Loss Function: Mean Absolute Error (MAE)

Optimizer: Adam

Evaluation Metric: MAE ≈ 4.27 minutes

Training Data: Historical GPS traces enriched with contextual data

🧪 Example Code Snippet
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# LSTM Model
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(time_steps, feature_dim)),
    Dropout(0.2),
    LSTM(32),
    Dense(1, activation='linear')
])

model.compile(optimizer='adam', loss='mae')
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_val, y_val))

🌐 Streamlit Dashboard Features

🚌 Live Bus Tracking: Displays real-time bus location updates.

📅 ETA Prediction: Shows expected arrival time based on model output.

🌤️ Weather Context: Integrates live weather conditions.

🚦 Traffic Visualization: Uses color-coded route congestion indicators.

📊 Performance Metrics: Displays model evaluation results interactively.

📈 Results
Metric	Value
Mean Absolute Error (MAE)	4.27 minutes
Model	LSTM
Deployment	Streamlit App
Integration	Real-time Traffic + Weather APIs
🚀 Future Work

Extend to multi-route and multi-city datasets.

Incorporate Graph Neural Networks (GNNs) for spatiotemporal modeling.

Optimize for edge deployment on onboard bus systems.

🧑‍💻 Developer & Research Intern

Nalina S D
🎓 Final-year ECE Student, PES University
📍 Internship: PESU Rapid Research Center (June 2025 – July 2025)
📝 Co-author: “Real-Time Bus Arrival Prediction Using LSTM with Traffic and Weather Integration” (AIMLSystems 2025 Submission)
