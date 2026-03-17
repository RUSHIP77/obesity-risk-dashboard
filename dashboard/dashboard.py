import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import joblib
import os

# ============================================================
# Load All Models and Data
# ============================================================
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)

dt_model = joblib.load(os.path.join(PROJECT, 'outputs/models/decision_tree_model.pkl'))
knn_model = joblib.load(os.path.join(PROJECT, 'outputs/models/knn_model.pkl'))
lr_model = joblib.load(os.path.join(PROJECT, 'outputs/models/linear_regression_model.pkl'))
km_model = joblib.load(os.path.join(PROJECT, 'outputs/models/kmeans_model.pkl'))
scaler_cls = joblib.load(os.path.join(PROJECT, 'outputs/models/scaler_classification.pkl'))
scaler_reg = joblib.load(os.path.join(PROJECT, 'outputs/models/scaler_regression.pkl'))
scaler_cluster = joblib.load(os.path.join(PROJECT, 'outputs/models/scaler_clustering.pkl'))
feature_names_cls = joblib.load(os.path.join(PROJECT, 'outputs/models/feature_names_classification.pkl'))
feature_names_reg = joblib.load(os.path.join(PROJECT, 'outputs/models/feature_names_regression.pkl'))
feature_names_cluster = joblib.load(os.path.join(PROJECT, 'outputs/models/feature_names_clustering.pkl'))
label_mapping = joblib.load(os.path.join(PROJECT, 'outputs/models/label_mapping.pkl'))
reverse_label_mapping = joblib.load(os.path.join(PROJECT, 'outputs/models/reverse_label_mapping.pkl'))
pca_model = joblib.load(os.path.join(PROJECT, 'outputs/models/pca_model.pkl'))
cluster_names = joblib.load(os.path.join(PROJECT, 'outputs/data/cluster_names.pkl'))

df = pd.read_csv(os.path.join(PROJECT, 'data/ObesityDataSet_raw_and_data_sinthetic.csv'))
df['BMI'] = df['Weight'] / (df['Height'] ** 2)
df_processed = pd.read_csv(os.path.join(PROJECT, 'outputs/data/processed_data.csv'))
cluster_profiles = pd.read_csv(os.path.join(PROJECT, 'outputs/data/cluster_profiles.csv'))
cluster_labels = joblib.load(os.path.join(PROJECT, 'outputs/data/cluster_labels.pkl'))

OBESITY_ORDER = ['Insufficient_Weight', 'Normal_Weight', 'Overweight_Level_I',
                 'Overweight_Level_II', 'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III']

OBESITY_COLORS = {
    'Insufficient_Weight': '#2196F3', 'Normal_Weight': '#4CAF50',
    'Overweight_Level_I': '#FFC107', 'Overweight_Level_II': '#FF9800',
    'Obesity_Type_I': '#FF5722', 'Obesity_Type_II': '#F44336',
    'Obesity_Type_III': '#B71C1C'
}

RISK_BADGE_COLORS = {
    'Insufficient_Weight': 'info', 'Normal_Weight': 'success',
    'Overweight_Level_I': 'warning', 'Overweight_Level_II': 'warning',
    'Obesity_Type_I': 'danger', 'Obesity_Type_II': 'danger',
    'Obesity_Type_III': 'danger'
}

# ============================================================
# App Setup
# ============================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True)
app.title = "Childhood Obesity Risk Screening Dashboard"

# ============================================================
# Tab 1: Overview
# ============================================================
avg_bmi = df['BMI'].mean()

kpi_cards = dbc.Row([
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4("2,111", className="card-title text-primary", style={"fontSize": "2rem"}),
            html.P("Total Records", className="card-text text-muted")
        ])
    ], className="text-center shadow-sm"), md=3),
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4("17", className="card-title text-success", style={"fontSize": "2rem"}),
            html.P("Features", className="card-text text-muted")
        ])
    ], className="text-center shadow-sm"), md=3),
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4("7", className="card-title text-warning", style={"fontSize": "2rem"}),
            html.P("Obesity Classes", className="card-text text-muted")
        ])
    ], className="text-center shadow-sm"), md=3),
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4(f"{avg_bmi:.1f}", className="card-title text-danger", style={"fontSize": "2rem"}),
            html.P("Avg BMI", className="card-text text-muted")
        ])
    ], className="text-center shadow-sm"), md=3),
], className="mb-4")

# Pie chart
counts = df['NObeyesdad'].value_counts().reindex(OBESITY_ORDER)
fig_pie = px.pie(values=counts.values, names=counts.index,
                 color=counts.index, color_discrete_map=OBESITY_COLORS,
                 title="Obesity Level Distribution")

# BMI histogram
fig_bmi_hist = px.histogram(df, x='BMI', color='NObeyesdad',
                             category_orders={'NObeyesdad': OBESITY_ORDER},
                             color_discrete_map=OBESITY_COLORS,
                             title="BMI Distribution by Obesity Level",
                             nbins=50)

tab1_content = dbc.Container([
    html.Br(),
    html.P("This dashboard presents results from a machine learning analysis of 2,111 individual records "
           "examining the relationship between lifestyle factors and obesity levels. The data comes from survey "
           "responses in Colombia, Peru, and Mexico, augmented with synthetic records via SMOTE.",
           className="text-muted"),
    kpi_cards,
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_pie), md=6),
        dbc.Col(dcc.Graph(figure=fig_bmi_hist), md=6),
    ])
], fluid=True)

# ============================================================
# Tab 2: Risk Factor Explorer
# ============================================================
numeric_features = ['Age', 'Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE', 'BMI']
all_features = numeric_features + ['Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE', 'SCC', 'CALC', 'MTRANS']

tab2_content = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H5("Feature Distribution by Obesity Level"),
            dcc.Dropdown(id='feature-select', options=[{'label': f, 'value': f} for f in numeric_features],
                         value='BMI', clearable=False),
            dcc.Graph(id='feature-dist-graph')
        ], md=6),
        dbc.Col([
            html.H5("Scatter Plot Builder"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='scatter-x', options=[{'label': f, 'value': f} for f in numeric_features],
                                      value='Age', clearable=False), md=6),
                dbc.Col(dcc.Dropdown(id='scatter-y', options=[{'label': f, 'value': f} for f in numeric_features],
                                      value='Weight', clearable=False), md=6),
            ]),
            dcc.Graph(id='scatter-graph')
        ], md=6),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Feature Importance (Decision Tree)"),
            dcc.Graph(id='feat-imp-graph', figure=go.Figure(
                go.Bar(
                    y=feature_names_cls,
                    x=dt_model.feature_importances_,
                    orientation='h',
                    marker_color='#2196F3'
                )
            ).update_layout(
                title="Decision Tree Feature Importance",
                yaxis={'categoryorder': 'total ascending'},
                height=500
            ))
        ], md=6),
        dbc.Col([
            html.H5("Correlation Heatmap"),
            dcc.Graph(id='corr-heatmap', figure=go.Figure(
                go.Heatmap(
                    z=df[numeric_features].corr().values,
                    x=numeric_features, y=numeric_features,
                    colorscale='RdBu_r', zmid=0,
                    text=np.round(df[numeric_features].corr().values, 2),
                    texttemplate='%{text}', textfont={"size": 9}
                )
            ).update_layout(title="Feature Correlation Heatmap", height=500))
        ], md=6),
    ])
], fluid=True)

# ============================================================
# Tab 3: Model Results
# ============================================================
# Read metrics
with open(os.path.join(PROJECT, 'outputs/data/regression_metrics.txt'), 'r') as f:
    reg_metrics_text = f.read()
with open(os.path.join(PROJECT, 'outputs/data/dt_metrics.txt'), 'r') as f:
    dt_metrics_text = f.read()
with open(os.path.join(PROJECT, 'outputs/data/knn_metrics.txt'), 'r') as f:
    knn_metrics_text = f.read()

model_comparison_df = pd.read_csv(os.path.join(PROJECT, 'outputs/data/model_comparison.csv'))

# Regression coefficient chart
coef_df = pd.DataFrame({
    'Feature': feature_names_reg,
    'Coefficient': lr_model.coef_
}).sort_values('Coefficient')

fig_coef = go.Figure(go.Bar(
    y=coef_df['Feature'], x=coef_df['Coefficient'],
    orientation='h',
    marker_color=['#F44336' if c < 0 else '#2196F3' for c in coef_df['Coefficient']]
))
fig_coef.update_layout(title="Linear Regression Coefficients — Predicting BMI", height=450)

# DT confusion matrix
from sklearn.metrics import confusion_matrix
X_test_cls = joblib.load(os.path.join(PROJECT, 'outputs/data/classification_splits.pkl'))[1]
y_test_cls = joblib.load(os.path.join(PROJECT, 'outputs/data/classification_splits.pkl'))[3]
y_pred_dt = dt_model.predict(X_test_cls)
cm_dt = confusion_matrix(y_test_cls, y_pred_dt)

fig_cm_dt = go.Figure(go.Heatmap(
    z=cm_dt, x=OBESITY_ORDER, y=OBESITY_ORDER,
    colorscale='Blues', text=cm_dt, texttemplate='%{text}',
    textfont={"size": 12}
))
fig_cm_dt.update_layout(title="Decision Tree — Confusion Matrix",
                         xaxis_title="Predicted", yaxis_title="Actual", height=500)

# KNN confusion matrix
X_test_cls_scaled = joblib.load(os.path.join(PROJECT, 'outputs/data/classification_splits_scaled.pkl'))[1]
y_pred_knn = knn_model.predict(X_test_cls_scaled)
cm_knn = confusion_matrix(y_test_cls, y_pred_knn)

fig_cm_knn = go.Figure(go.Heatmap(
    z=cm_knn, x=OBESITY_ORDER, y=OBESITY_ORDER,
    colorscale='Blues', text=cm_knn, texttemplate='%{text}',
    textfont={"size": 12}
))
fig_cm_knn.update_layout(title="KNN — Confusion Matrix",
                          xaxis_title="Predicted", yaxis_title="Actual", height=500)

tab3_content = dbc.Container([
    html.Br(),
    html.H5("Model Comparison Table"),
    dash_table.DataTable(
        data=model_comparison_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in model_comparison_df.columns],
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}]
    ),
    html.Hr(),
    dbc.Accordion([
        dbc.AccordionItem([
            html.Pre(reg_metrics_text, style={"fontSize": "12px"}),
            dcc.Graph(figure=fig_coef)
        ], title="Linear Regression"),
        dbc.AccordionItem([
            html.Pre(dt_metrics_text, style={"fontSize": "12px"}),
            dcc.Graph(figure=fig_cm_dt)
        ], title="Decision Tree Classifier"),
        dbc.AccordionItem([
            html.Pre(knn_metrics_text, style={"fontSize": "12px"}),
            dcc.Graph(figure=fig_cm_knn)
        ], title="KNN Classifier"),
    ], start_collapsed=True)
], fluid=True)

# ============================================================
# Tab 4: Cluster Profiles
# ============================================================
# PCA scatter
X_cluster_scaled = joblib.load(os.path.join(PROJECT, 'outputs/data/clustering_data_scaled.pkl'))
X_pca = pca_model.transform(X_cluster_scaled)

pca_df = pd.DataFrame({
    'PC1': X_pca[:, 0], 'PC2': X_pca[:, 1],
    'Cluster': [f"Cluster {c}: {cluster_names.get(c, c)}" for c in cluster_labels]
})

fig_pca = px.scatter(pca_df, x='PC1', y='PC2', color='Cluster',
                      title="K-Means Clusters (PCA Projection)",
                      labels={'PC1': f'PC1 ({pca_model.explained_variance_ratio_[0]*100:.1f}%)',
                              'PC2': f'PC2 ({pca_model.explained_variance_ratio_[1]*100:.1f}%)'})

# Radar chart
radar_features = ['FAF', 'TUE', 'FCVC', 'FAVC', 'CH2O', 'NCP', 'CAEC', 'CALC']
radar_data = cluster_profiles[radar_features]
radar_norm = (radar_data - radar_data.min()) / (radar_data.max() - radar_data.min() + 1e-10)

fig_radar = go.Figure()
colors_radar = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0']
for i in range(len(cluster_profiles)):
    vals = radar_norm.iloc[i].tolist()
    vals += vals[:1]
    fig_radar.add_trace(go.Scatterpolar(
        r=vals, theta=radar_features + [radar_features[0]],
        fill='toself', name=f"Cluster {i}: {cluster_names.get(i, i)}",
        line_color=colors_radar[i % len(colors_radar)]
    ))
fig_radar.update_layout(title="Cluster Risk Profiles", height=500,
                         polar=dict(radialaxis=dict(range=[0, 1])))

tab4_content = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_pca), md=6),
        dbc.Col(dcc.Graph(figure=fig_radar), md=6),
    ]),
    html.Hr(),
    html.H5("Cluster Profile Summary (Mean Values)"),
    dash_table.DataTable(
        data=cluster_profiles.round(3).to_dict('records'),
        columns=[{"name": i, "id": i} for i in cluster_profiles.columns],
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center', 'padding': '8px', 'fontSize': '12px'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}]
    )
], fluid=True)

# ============================================================
# Tab 5: Screening Tool
# ============================================================
def make_input_form():
    return dbc.Card([
        dbc.CardHeader(html.H4("Enter Patient Information", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Gender"), dcc.Dropdown(id='inp-gender',
                        options=[{'label': 'Female', 'value': 'Female'}, {'label': 'Male', 'value': 'Male'}],
                        value='Female', clearable=False)
                ], md=3),
                dbc.Col([
                    dbc.Label("Age"), dbc.Input(id='inp-age', type='number', min=14, max=65, value=20)
                ], md=3),
                dbc.Col([
                    dbc.Label("Height (meters)"), dbc.Input(id='inp-height', type='number', min=1.0, max=2.2, step=0.01, value=1.65)
                ], md=3),
                dbc.Col([
                    dbc.Label("Weight (kg)"), dbc.Input(id='inp-weight', type='number', min=30, max=200, step=0.5, value=65)
                ], md=3),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Family History of Overweight"),
                    dcc.RadioItems(id='inp-fh', options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                                   value='yes', inline=True)
                ], md=4),
                dbc.Col([
                    dbc.Label("High Caloric Food (FAVC)"),
                    dcc.RadioItems(id='inp-favc', options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                                   value='yes', inline=True)
                ], md=4),
                dbc.Col([
                    dbc.Label("Smoking"),
                    dcc.RadioItems(id='inp-smoke', options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                                   value='no', inline=True)
                ], md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Vegetable Consumption (FCVC)"),
                    dcc.Slider(id='inp-fcvc', min=1, max=3, step=0.5, value=2,
                               marks={1: 'Never', 2: 'Sometimes', 3: 'Always'})
                ], md=4),
                dbc.Col([
                    dbc.Label("Meals per Day (NCP)"),
                    dcc.Slider(id='inp-ncp', min=1, max=4, step=1, value=3,
                               marks={1: '1', 2: '2', 3: '3', 4: '4+'})
                ], md=4),
                dbc.Col([
                    dbc.Label("Water Consumption (CH2O)"),
                    dcc.Slider(id='inp-ch2o', min=1, max=3, step=0.5, value=2,
                               marks={1: '<1L', 2: '1-2L', 3: '>2L'})
                ], md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Physical Activity (FAF)"),
                    dcc.Slider(id='inp-faf', min=0, max=3, step=1, value=1,
                               marks={0: 'None', 1: '1-2 days', 2: '2-4 days', 3: '4-5 days'})
                ], md=4),
                dbc.Col([
                    dbc.Label("Technology Use (TUE)"),
                    dcc.Slider(id='inp-tue', min=0, max=2, step=1, value=1,
                               marks={0: '0-2 hrs', 1: '3-5 hrs', 2: '5+ hrs'})
                ], md=4),
                dbc.Col([
                    dbc.Label("Calorie Monitoring (SCC)"),
                    dcc.RadioItems(id='inp-scc', options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                                   value='no', inline=True)
                ], md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Eating Between Meals (CAEC)"),
                    dcc.Dropdown(id='inp-caec',
                        options=[{'label': v, 'value': v} for v in ['no', 'Sometimes', 'Frequently', 'Always']],
                        value='Sometimes', clearable=False)
                ], md=4),
                dbc.Col([
                    dbc.Label("Alcohol Consumption (CALC)"),
                    dcc.Dropdown(id='inp-calc',
                        options=[{'label': v, 'value': v} for v in ['no', 'Sometimes', 'Frequently', 'Always']],
                        value='Sometimes', clearable=False)
                ], md=4),
                dbc.Col([
                    dbc.Label("Transportation (MTRANS)"),
                    dcc.Dropdown(id='inp-mtrans',
                        options=[{'label': v, 'value': v} for v in ['Automobile', 'Motorbike', 'Bike', 'Public_Transportation', 'Walking']],
                        value='Public_Transportation', clearable=False)
                ], md=4),
            ], className="mb-3"),
            html.Div(className="d-grid gap-2", children=[
                dbc.Button("Predict Obesity Risk", id="predict-btn", color="primary", size="lg", className="mt-3")
            ])
        ])
    ], className="shadow-sm")

tab5_content = dbc.Container([
    html.Br(),
    html.P("Enter lifestyle and demographic information below to receive a personalized obesity risk assessment. "
           "This tool uses trained machine learning models to predict obesity risk level, estimated BMI, "
           "and behavioral risk cluster.", className="text-muted"),
    make_input_form(),
    html.Br(),
    html.Div(id='prediction-output')
], fluid=True)

# ============================================================
# Main Layout
# ============================================================
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Childhood Obesity Risk Screening Dashboard",
        brand_style={"fontSize": "1.5rem", "fontWeight": "bold"},
        color="primary", dark=True, className="mb-4"
    ),
    dbc.Tabs([
        dbc.Tab(tab1_content, label="Overview", tab_id="tab-overview"),
        dbc.Tab(tab2_content, label="Risk Factor Explorer", tab_id="tab-risk"),
        dbc.Tab(tab3_content, label="Model Results", tab_id="tab-models"),
        dbc.Tab(tab4_content, label="Cluster Profiles", tab_id="tab-clusters"),
        dbc.Tab(tab5_content, label="Screening Tool", tab_id="tab-screening"),
    ]),
    html.Footer([
        html.Hr(),
        html.P("DSC 510 Final Project | Group 2: Rushi Patel, Raffey Akram, Vishnu Doddapaneni | "
               "Prof. Casey Bennett | DePaul University",
               className="text-center text-muted"),
        html.P("This tool is for educational and research purposes only. Not a substitute for medical advice.",
               className="text-center text-muted", style={"fontSize": "0.8rem"})
    ])
], fluid=True)

# ============================================================
# Callbacks
# ============================================================
@app.callback(
    Output('feature-dist-graph', 'figure'),
    Input('feature-select', 'value')
)
def update_feature_dist(feature):
    fig = px.box(df, x='NObeyesdad', y=feature,
                 category_orders={'NObeyesdad': OBESITY_ORDER},
                 color='NObeyesdad', color_discrete_map=OBESITY_COLORS,
                 title=f'{feature} Distribution by Obesity Level')
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    return fig

@app.callback(
    Output('scatter-graph', 'figure'),
    [Input('scatter-x', 'value'), Input('scatter-y', 'value')]
)
def update_scatter(x_feat, y_feat):
    fig = px.scatter(df, x=x_feat, y=y_feat, color='NObeyesdad',
                     category_orders={'NObeyesdad': OBESITY_ORDER},
                     color_discrete_map=OBESITY_COLORS,
                     title=f'{x_feat} vs {y_feat} by Obesity Level',
                     opacity=0.6)
    return fig

@app.callback(
    Output('prediction-output', 'children'),
    Input('predict-btn', 'n_clicks'),
    [State('inp-gender', 'value'), State('inp-age', 'value'),
     State('inp-height', 'value'), State('inp-weight', 'value'),
     State('inp-fh', 'value'), State('inp-favc', 'value'),
     State('inp-fcvc', 'value'), State('inp-ncp', 'value'),
     State('inp-caec', 'value'), State('inp-smoke', 'value'),
     State('inp-ch2o', 'value'), State('inp-scc', 'value'),
     State('inp-faf', 'value'), State('inp-tue', 'value'),
     State('inp-calc', 'value'), State('inp-mtrans', 'value')],
    prevent_initial_call=True
)
def predict(n_clicks, gender, age, height, weight, fh, favc,
            fcvc, ncp, caec, smoke, ch2o, scc, faf, tue, calc, mtrans):
    try:
        if any(v is None for v in [gender, age, height, weight]):
            return dbc.Alert("Please fill in all required fields.", color="warning")

        age = float(age)
        height = float(height)
        weight = float(weight)

        # Encode inputs
        gender_enc = 1 if gender == 'Male' else 0
        fh_enc = 1 if fh == 'yes' else 0
        favc_enc = 1 if favc == 'yes' else 0
        smoke_enc = 1 if smoke == 'yes' else 0
        scc_enc = 1 if scc == 'yes' else 0

        caec_map = {'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3}
        calc_map = {'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3}
        caec_enc = caec_map.get(caec, 1)
        calc_enc = calc_map.get(calc, 1)

        mtrans_bike = 1 if mtrans == 'Bike' else 0
        mtrans_motorbike = 1 if mtrans == 'Motorbike' else 0
        mtrans_public = 1 if mtrans == 'Public_Transportation' else 0
        mtrans_walking = 1 if mtrans == 'Walking' else 0

        bmi = weight / (height ** 2)
        activity_screen_ratio = faf / (tue + 0.1)
        dietary_risk_score = favc_enc + (3 - fcvc) + caec_enc

        # Build classification features (MUST match feature_names_cls order)
        cls_dict = {
            'Gender': gender_enc, 'Age': age, 'Height': height, 'Weight': weight,
            'family_history_with_overweight': fh_enc, 'FAVC': favc_enc,
            'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec_enc, 'SMOKE': smoke_enc,
            'CH2O': ch2o, 'SCC': scc_enc, 'FAF': faf, 'TUE': tue, 'CALC': calc_enc,
            'BMI': bmi, 'Activity_Screen_Ratio': activity_screen_ratio,
            'Dietary_Risk_Score': dietary_risk_score,
            'MTRANS_Bike': mtrans_bike, 'MTRANS_Motorbike': mtrans_motorbike,
            'MTRANS_Public_Transportation': mtrans_public, 'MTRANS_Walking': mtrans_walking
        }
        cls_features = pd.DataFrame([cls_dict])[feature_names_cls]

        # Build regression features
        reg_dict = {
            'Gender': gender_enc, 'Age': age,
            'family_history_with_overweight': fh_enc, 'FAVC': favc_enc,
            'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec_enc, 'SMOKE': smoke_enc,
            'CH2O': ch2o, 'SCC': scc_enc, 'FAF': faf, 'TUE': tue, 'CALC': calc_enc,
            'MTRANS_Bike': mtrans_bike, 'MTRANS_Motorbike': mtrans_motorbike,
            'MTRANS_Public_Transportation': mtrans_public, 'MTRANS_Walking': mtrans_walking
        }
        reg_features = pd.DataFrame([reg_dict])[feature_names_reg]

        # Build clustering features
        cluster_dict = {
            'Gender': gender_enc, 'Age': age,
            'family_history_with_overweight': fh_enc, 'FAVC': favc_enc,
            'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec_enc, 'SMOKE': smoke_enc,
            'CH2O': ch2o, 'SCC': scc_enc, 'FAF': faf, 'TUE': tue, 'CALC': calc_enc
        }
        cluster_features = pd.DataFrame([cluster_dict])[feature_names_cluster]

        # Scale and predict
        cls_scaled = scaler_cls.transform(cls_features)
        reg_scaled = scaler_reg.transform(reg_features)
        cluster_scaled_input = scaler_cluster.transform(cluster_features)

        # Decision Tree prediction (unscaled)
        dt_pred = dt_model.predict(cls_features)[0]
        predicted_class = reverse_label_mapping[dt_pred]

        # BMI prediction
        predicted_bmi = lr_model.predict(reg_scaled)[0]

        # Cluster assignment
        cluster_pred = km_model.predict(cluster_scaled_input)[0]
        cluster_name = cluster_names.get(cluster_pred, f"Cluster {cluster_pred}")

        # Risk factors and recommendations
        recommendations = []
        risk_factors = []

        if faf <= 1:
            risk_factors.append("Low physical activity")
            recommendations.append("Consider increasing physical activity to at least 2-4 days per week")
        if tue >= 2:
            risk_factors.append("High screen/technology time")
            recommendations.append("Consider reducing screen/technology time to under 2 hours per day")
        if fcvc < 2:
            risk_factors.append("Low vegetable consumption")
            recommendations.append("Increase daily vegetable consumption")
        if ch2o < 2:
            risk_factors.append("Low water intake")
            recommendations.append("Increase water intake to at least 2 liters per day")
        if favc == 'yes':
            risk_factors.append("Frequent high-calorie food consumption")
            recommendations.append("Reduce consumption of high-calorie foods")
        if fh == 'yes':
            risk_factors.append("Family history of overweight")
            recommendations.append("Monitor weight closely due to family history; focus on preventive lifestyle habits")

        if not risk_factors:
            risk_factors = ["No major modifiable risk factors identified"]
        if not recommendations:
            recommendations = ["Continue maintaining healthy lifestyle habits"]

        badge_color = RISK_BADGE_COLORS.get(predicted_class, 'secondary')

        result = dbc.Card([
            dbc.CardHeader(html.H4("Prediction Results", className="mb-0 text-white"),
                          style={"backgroundColor": "#2c3e50"}),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5("Predicted Risk Level"),
                        dbc.Badge(predicted_class.replace('_', ' '), color=badge_color,
                                  className="p-3", style={"fontSize": "1.2rem"}),
                    ], md=4, className="text-center"),
                    dbc.Col([
                        html.H5("Predicted BMI"),
                        html.H3(f"{predicted_bmi:.1f} kg/m²", className="text-primary"),
                        html.P(f"Actual BMI (from inputs): {bmi:.1f} kg/m²", className="text-muted small")
                    ], md=4, className="text-center"),
                    dbc.Col([
                        html.H5("Behavioral Cluster"),
                        html.H4(cluster_name, className="text-info"),
                    ], md=4, className="text-center"),
                ], className="mb-4"),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H5("Top Risk Factors", className="text-danger"),
                        html.Ul([html.Li(rf) for rf in risk_factors[:3]])
                    ], md=6),
                    dbc.Col([
                        html.H5("Personalized Recommendations", className="text-success"),
                        html.Ul([html.Li(r) for r in recommendations[:4]])
                    ], md=6),
                ])
            ])
        ], className="shadow")

        return result

    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


server = app.server  # Required for production deployment (Gunicorn)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"Starting dashboard on http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
