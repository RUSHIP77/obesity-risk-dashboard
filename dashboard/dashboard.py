import matplotlib
matplotlib.use('Agg')
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
import joblib
import os

# ============================================================
# Paths
# ============================================================
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)

# ============================================================
# Custom Plotly Template
# ============================================================
CHART_COLORS = ["#3B9AE8", "#2DD4BF", "#FBBF24", "#A78BFA",
                "#34D399", "#F472B6", "#FB923C", "#94A3B8"]

pio.templates["health_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color="#94A3B8"),
        title=dict(font=dict(family="Manrope, sans-serif", size=17,
                              color="#F1F5F9"), x=0, xanchor="left",
                   pad=dict(l=4, t=4)),
        xaxis=dict(
            gridcolor="rgba(42,47,69,0.5)", gridwidth=1, griddash="dot",
            zeroline=False, linecolor="#2A2F45", linewidth=1,
            tickfont=dict(size=11, color="#64748B"),
            title_font=dict(size=13, color="#94A3B8"),
        ),
        yaxis=dict(
            gridcolor="rgba(42,47,69,0.5)", gridwidth=1, griddash="dot",
            zeroline=False, linecolor="#2A2F45", linewidth=1,
            tickfont=dict(size=11, color="#64748B"),
            title_font=dict(size=13, color="#94A3B8"),
        ),
        colorway=CHART_COLORS,
        legend=dict(
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            font=dict(size=13, color="#CBD5E1"),
        ),
        hoverlabel=dict(
            bgcolor="#1E2235", bordercolor="#2A2F45",
            font=dict(family="Inter, sans-serif", size=13, color="#F1F5F9"),
        ),
        margin=dict(l=48, r=16, t=56, b=48),
    ),
    data=dict(
        bar=[go.Bar(marker=dict(cornerradius=4, line=dict(width=0)))],
        scatter=[go.Scatter(marker=dict(size=8, line=dict(width=1, color="#141821")))],
    ),
)
pio.templates.default = "health_dark"
CHART_CONFIG = {"displayModeBar": False, "scrollZoom": False, "responsive": True}

# ============================================================
# Load Models & Data
# ============================================================
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
    'Insufficient_Weight': '#60A5FA', 'Normal_Weight': '#34D399',
    'Overweight_Level_I': '#FBBF24', 'Overweight_Level_II': '#FB923C',
    'Obesity_Type_I': '#F87171', 'Obesity_Type_II': '#EF4444',
    'Obesity_Type_III': '#DC2626'
}

# Clean display names (no underscores)
OBESITY_LABELS = {c: c.replace('_', ' ') for c in OBESITY_ORDER}
df['Obesity_Label'] = df['NObeyesdad'].map(OBESITY_LABELS)
LABEL_ORDER = [OBESITY_LABELS[c] for c in OBESITY_ORDER]
LABEL_COLORS = {OBESITY_LABELS[k]: v for k, v in OBESITY_COLORS.items()}

# Clean feature names for display
def clean_feature_name(name):
    return name.replace('_', ' ').replace('MTRANS ', 'Transport: ').replace('family history with overweight', 'Family History')

RISK_CSS = {
    'Insufficient_Weight': 'risk-low', 'Normal_Weight': 'risk-low',
    'Overweight_Level_I': 'risk-moderate', 'Overweight_Level_II': 'risk-moderate',
    'Obesity_Type_I': 'risk-high', 'Obesity_Type_II': 'risk-critical',
    'Obesity_Type_III': 'risk-critical'
}

# ============================================================
# App Setup
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap"
    ],
    suppress_callback_exceptions=True
)
app.title = "Childhood Obesity Risk Screening Dashboard"

# ============================================================
# Tab 1: Overview
# ============================================================
avg_bmi = df['BMI'].mean()
obesity_most = df['NObeyesdad'].value_counts().idxmax()
fh_pct = (df['family_history_with_overweight'] == 'yes').mean() * 100

kpi_row = dbc.Row([
    dbc.Col(html.Div([
        html.Div("📊", className="kpi-icon blue"),
        html.Div("2,111", className="kpi-value"),
        html.Div("Total Records", className="kpi-label"),
    ], className="kpi-card fade-in-d1"), xs=6, md=3),
    dbc.Col(html.Div([
        html.Div("🔬", className="kpi-icon teal"),
        html.Div("17", className="kpi-value"),
        html.Div("Features", className="kpi-label"),
    ], className="kpi-card fade-in-d2"), xs=6, md=3),
    dbc.Col(html.Div([
        html.Div("📈", className="kpi-icon amber"),
        html.Div("7", className="kpi-value"),
        html.Div("Obesity Classes", className="kpi-label"),
    ], className="kpi-card fade-in-d3"), xs=6, md=3),
    dbc.Col(html.Div([
        html.Div("⚖️", className="kpi-icon red"),
        html.Div(f"{avg_bmi:.1f}", className="kpi-value"),
        html.Div("Average BMI", className="kpi-label"),
    ], className="kpi-card fade-in-d4"), xs=6, md=3),
], className="g-3 mb-4")

# Donut chart
counts = df['NObeyesdad'].value_counts().reindex(OBESITY_ORDER)
fig_donut = go.Figure(data=[go.Pie(
    labels=[c.replace('_', ' ') for c in counts.index],
    values=counts.values, hole=0.55,
    marker=dict(colors=[OBESITY_COLORS[c] for c in counts.index],
                line=dict(color='#141821', width=2)),
    textinfo='percent', textfont=dict(size=12, color='#F1F5F9'),
    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>',
)])
fig_donut.add_annotation(text=f"<b>Total</b><br>{len(df):,}",
                          font=dict(size=16, color="#F1F5F9", family="Manrope"),
                          showarrow=False)
fig_donut.update_layout(title="Obesity Level Distribution", height=420,
                         legend=dict(font=dict(size=11)))

# BMI Histogram
fig_bmi = px.histogram(df, x='BMI', color='Obesity_Label',
                        category_orders={'Obesity_Label': LABEL_ORDER},
                        color_discrete_map=LABEL_COLORS,
                        title="BMI Distribution by Obesity Level", nbins=50)
fig_bmi.update_layout(height=420, legend_title_text="",
                       legend=dict(font=dict(size=12, color="#CBD5E1")),
                       xaxis_title="BMI (kg/m²)", yaxis_title="Count")

tab1 = dbc.Container([
    html.Div(style={"height": "16px"}),
    html.P("Machine learning analysis of 2,111 records examining lifestyle factors and obesity levels. "
           "Data from Colombia, Peru, and Mexico, augmented with synthetic records via SMOTE.",
           className="section-subtitle"),
    kpi_row,
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Graph(figure=fig_donut, config=CHART_CONFIG)
        ], className="chart-container"), md=6),
        dbc.Col(html.Div([
            dcc.Graph(figure=fig_bmi, config=CHART_CONFIG)
        ], className="chart-container"), md=6),
    ], className="g-3"),
], fluid=True)

# ============================================================
# Tab 2: Risk Factor Explorer
# ============================================================
numeric_features = ['Age', 'Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE', 'BMI']

# Feature importance
feat_imp_df = pd.DataFrame({
    'Feature': [clean_feature_name(f) for f in feature_names_cls],
    'Importance': dt_model.feature_importances_
}).sort_values('Importance', ascending=True).tail(12)

fig_feat_imp = go.Figure(go.Bar(
    y=feat_imp_df['Feature'], x=feat_imp_df['Importance'],
    orientation='h',
    marker=dict(
        color=feat_imp_df['Importance'],
        colorscale=[[0, '#1A3A5C'], [1, '#3B9AE8']],
        cornerradius=6
    ),
))
fig_feat_imp.update_layout(title="Decision Tree — Feature Importance (Top 12)",
                            height=450, showlegend=False,
                            xaxis_title="Importance Score",
                            margin=dict(l=180, r=16, t=56, b=48))

# Correlation heatmap
corr_vals = df[numeric_features].corr().values
fig_corr = go.Figure(go.Heatmap(
    z=corr_vals, x=numeric_features, y=numeric_features,
    colorscale=[[0, "#F87171"], [0.5, "#1E2235"], [1, "#3B9AE8"]],
    zmid=0,
    text=np.round(corr_vals, 2), texttemplate='%{text}',
    textfont={"size": 10, "color": "#F1F5F9"},
    xgap=2, ygap=2, showscale=True,
    colorbar=dict(tickfont=dict(color="#64748B")),
))
fig_corr.update_layout(title="Feature Correlation Heatmap", height=450,
                        margin=dict(l=48, r=60, t=56, b=48))

tab2 = dbc.Container([
    html.Div(style={"height": "16px"}),
    dbc.Row([
        dbc.Col(html.Div([
            html.Div("Feature Distribution by Obesity Level", className="chart-title"),
            dcc.Dropdown(id='feature-select',
                         options=[{'label': f, 'value': f} for f in numeric_features],
                         value='BMI', clearable=False,
                         style={"marginBottom": "12px"}),
            dcc.Graph(id='feature-dist-graph', config=CHART_CONFIG)
        ], className="chart-container"), md=6),
        dbc.Col(html.Div([
            html.Div("Scatter Plot Builder", className="chart-title"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='scatter-x',
                    options=[{'label': f, 'value': f} for f in numeric_features],
                    value='Age', clearable=False), md=6),
                dbc.Col(dcc.Dropdown(id='scatter-y',
                    options=[{'label': f, 'value': f} for f in numeric_features],
                    value='Weight', clearable=False), md=6),
            ], style={"marginBottom": "12px"}),
            dcc.Graph(id='scatter-graph', config=CHART_CONFIG)
        ], className="chart-container"), md=6),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Graph(figure=fig_feat_imp, config=CHART_CONFIG)
        ], className="chart-container"), md=6),
        dbc.Col(html.Div([
            dcc.Graph(figure=fig_corr, config=CHART_CONFIG)
        ], className="chart-container"), md=6),
    ], className="g-3"),
], fluid=True)

# ============================================================
# Tab 3: Model Results
# ============================================================
with open(os.path.join(PROJECT, 'outputs/data/regression_metrics.txt'), 'r') as f:
    reg_metrics_text = f.read()
with open(os.path.join(PROJECT, 'outputs/data/dt_metrics.txt'), 'r') as f:
    dt_metrics_text = f.read()
with open(os.path.join(PROJECT, 'outputs/data/knn_metrics.txt'), 'r') as f:
    knn_metrics_text = f.read()

model_comparison_df = pd.read_csv(os.path.join(PROJECT, 'outputs/data/model_comparison.csv'))

# Regression coefficients
coef_df = pd.DataFrame({
    'Feature': feature_names_reg, 'Coefficient': lr_model.coef_
}).sort_values('Coefficient')
fig_coef = go.Figure(go.Bar(
    y=coef_df['Feature'], x=coef_df['Coefficient'], orientation='h',
    marker=dict(
        color=['#F87171' if c < 0 else '#3B9AE8' for c in coef_df['Coefficient']],
        cornerradius=6
    ),
))
fig_coef.update_layout(title="Linear Regression Coefficients — Predicting BMI", height=420)

# Confusion matrices
from sklearn.metrics import confusion_matrix
X_test_cls = joblib.load(os.path.join(PROJECT, 'outputs/data/classification_splits.pkl'))[1]
y_test_cls = joblib.load(os.path.join(PROJECT, 'outputs/data/classification_splits.pkl'))[3]
X_test_cls_scaled = joblib.load(os.path.join(PROJECT, 'outputs/data/classification_splits_scaled.pkl'))[1]

labels_short = [c.replace('_', ' ').replace('Level ', 'L').replace('Type ', 'T') for c in OBESITY_ORDER]

cm_dt = confusion_matrix(y_test_cls, dt_model.predict(X_test_cls))
fig_cm_dt = go.Figure(go.Heatmap(
    z=cm_dt, x=labels_short, y=labels_short,
    colorscale=[[0, "#141821"], [0.5, "#1A3A5C"], [1, "#3B9AE8"]],
    text=cm_dt, texttemplate='%{text}', textfont=dict(size=13, color="#F1F5F9"),
    xgap=3, ygap=3, showscale=False,
))
fig_cm_dt.update_layout(title="Decision Tree — Confusion Matrix", height=420,
                         xaxis_title="Predicted", yaxis_title="Actual")

cm_knn = confusion_matrix(y_test_cls, knn_model.predict(X_test_cls_scaled))
fig_cm_knn = go.Figure(go.Heatmap(
    z=cm_knn, x=labels_short, y=labels_short,
    colorscale=[[0, "#141821"], [0.5, "#1A3A5C"], [1, "#2DD4BF"]],
    text=cm_knn, texttemplate='%{text}', textfont=dict(size=13, color="#F1F5F9"),
    xgap=3, ygap=3, showscale=False,
))
fig_cm_knn.update_layout(title="KNN — Confusion Matrix", height=420,
                          xaxis_title="Predicted", yaxis_title="Actual")

tab3 = dbc.Container([
    html.Div(style={"height": "16px"}),
    html.Div("Model Comparison", className="section-header"),
    html.Div([
        dash_table.DataTable(
            data=model_comparison_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in model_comparison_df.columns],
            style_header={'backgroundColor': 'rgba(59,154,232,0.1)', 'color': '#3B9AE8',
                          'fontWeight': '600', 'textTransform': 'uppercase', 'fontSize': '11px',
                          'letterSpacing': '0.5px', 'border': '1px solid #2A2F45'},
            style_cell={'textAlign': 'center', 'padding': '14px 16px',
                        'backgroundColor': '#1E2235', 'color': '#F1F5F9',
                        'border': '1px solid #2A2F45', 'fontFamily': 'Inter, sans-serif',
                        'fontSize': '13px'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#1A1D2E'}
            ]
        )
    ], className="glass-card mb-4", style={"padding": "0", "overflow": "hidden"}),
    dbc.Accordion([
        dbc.AccordionItem([
            html.Pre(reg_metrics_text,
                     style={"fontSize": "12px", "color": "#94A3B8", "background": "transparent",
                            "border": "none", "fontFamily": "JetBrains Mono, monospace"}),
            html.Div([dcc.Graph(figure=fig_coef, config=CHART_CONFIG)], className="chart-container")
        ], title="📈  Linear Regression — R² = 0.466"),
        dbc.AccordionItem([
            html.Pre(dt_metrics_text,
                     style={"fontSize": "12px", "color": "#94A3B8", "background": "transparent",
                            "border": "none", "fontFamily": "JetBrains Mono, monospace"}),
            html.Div([dcc.Graph(figure=fig_cm_dt, config=CHART_CONFIG)], className="chart-container")
        ], title="🌳  Decision Tree — 96.7% Accuracy"),
        dbc.AccordionItem([
            html.Pre(knn_metrics_text,
                     style={"fontSize": "12px", "color": "#94A3B8", "background": "transparent",
                            "border": "none", "fontFamily": "JetBrains Mono, monospace"}),
            html.Div([dcc.Graph(figure=fig_cm_knn, config=CHART_CONFIG)], className="chart-container")
        ], title="🔍  KNN Classifier — 86.1% Accuracy"),
    ], start_collapsed=True),
], fluid=True)

# ============================================================
# Tab 4: Cluster Profiles
# ============================================================
X_cluster_scaled = joblib.load(os.path.join(PROJECT, 'outputs/data/clustering_data_scaled.pkl'))
X_pca = pca_model.transform(X_cluster_scaled)
pca_df = pd.DataFrame({
    'PC1': X_pca[:, 0], 'PC2': X_pca[:, 1],
    'Cluster': [f"Cluster {c}: {cluster_names.get(c, c)}" for c in cluster_labels]
})

fig_pca = px.scatter(pca_df, x='PC1', y='PC2', color='Cluster',
                      title="K-Means Clusters (PCA Projection)",
                      color_discrete_sequence=CHART_COLORS,
                      opacity=0.65,
                      labels={'PC1': f'PC1 ({pca_model.explained_variance_ratio_[0]*100:.1f}%)',
                              'PC2': f'PC2 ({pca_model.explained_variance_ratio_[1]*100:.1f}%)'})
fig_pca.update_traces(marker=dict(size=7, line=dict(width=1, color='#141821')))
fig_pca.update_layout(height=460, legend=dict(font=dict(size=12, color="#CBD5E1")))

# Radar chart
radar_features = ['FAF', 'TUE', 'FCVC', 'FAVC', 'CH2O', 'NCP', 'CAEC', 'CALC']
radar_data = cluster_profiles[radar_features]
radar_norm = (radar_data - radar_data.min()) / (radar_data.max() - radar_data.min() + 1e-10)

RADAR_FILLS = [
    "rgba(59,154,232,0.12)", "rgba(45,212,191,0.12)",
    "rgba(251,191,36,0.12)", "rgba(167,139,250,0.12)",
]
fig_radar = go.Figure()
for i in range(len(cluster_profiles)):
    vals = radar_norm.iloc[i].tolist() + [radar_norm.iloc[i].tolist()[0]]
    fig_radar.add_trace(go.Scatterpolar(
        r=vals, theta=radar_features + [radar_features[0]],
        fill='toself', name=f"Cluster {i}: {cluster_names.get(i, i)}",
        line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
        fillcolor=RADAR_FILLS[i % len(RADAR_FILLS)],
        opacity=0.85,
    ))
fig_radar.update_layout(
    title="Cluster Risk Profiles", height=460,
    polar=dict(
        bgcolor='rgba(0,0,0,0)',
        radialaxis=dict(range=[0, 1], gridcolor='#2A2F45', linecolor='#2A2F45',
                        tickfont=dict(size=10, color="#64748B")),
        angularaxis=dict(gridcolor='#2A2F45', linecolor='#2A2F45',
                         tickfont=dict(size=12, color="#94A3B8")),
    ),
    legend=dict(font=dict(size=12, color="#CBD5E1")),
)

tab4 = dbc.Container([
    html.Div(style={"height": "16px"}),
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Graph(figure=fig_pca, config=CHART_CONFIG)
        ], className="chart-container"), md=6),
        dbc.Col(html.Div([
            dcc.Graph(figure=fig_radar, config=CHART_CONFIG)
        ], className="chart-container"), md=6),
    ], className="g-3 mb-3"),
    html.Div("Cluster Profile Summary", className="section-header"),
    html.Div([
        dash_table.DataTable(
            data=cluster_profiles.round(3).to_dict('records'),
            columns=[{"name": i, "id": i} for i in cluster_profiles.columns],
            style_header={'backgroundColor': 'rgba(59,154,232,0.1)', 'color': '#3B9AE8',
                          'fontWeight': '600', 'textTransform': 'uppercase', 'fontSize': '11px',
                          'letterSpacing': '0.5px', 'border': '1px solid #2A2F45'},
            style_cell={'textAlign': 'center', 'padding': '12px 14px',
                        'backgroundColor': '#1E2235', 'color': '#F1F5F9',
                        'border': '1px solid #2A2F45', 'fontFamily': 'Inter, sans-serif',
                        'fontSize': '12px'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#1A1D2E'}
            ]
        )
    ], className="glass-card", style={"padding": "0", "overflow": "hidden"}),
], fluid=True)

# ============================================================
# Tab 5: Screening Tool
# ============================================================
def make_dropdown(id, options, value):
    return dcc.Dropdown(id=id, options=[{'label': v, 'value': v} for v in options],
                        value=value, clearable=False)

tab5 = dbc.Container([
    html.Div(style={"height": "16px"}),
    html.P("Enter lifestyle and demographic information to receive a personalized obesity risk assessment "
           "powered by trained machine learning models.",
           className="section-subtitle"),

    # Section 1: Physical Profile
    html.Div([
        html.Div("Physical Profile", className="form-section-title"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Gender", className="form-label"),
                make_dropdown('inp-gender', ['Female', 'Male'], 'Female')
            ], xs=6, md=3),
            dbc.Col([
                dbc.Label("Age", className="form-label"),
                dbc.Input(id='inp-age', type='number', min=14, max=65, value=20)
            ], xs=6, md=3),
            dbc.Col([
                dbc.Label("Height (m)", className="form-label"),
                dbc.Input(id='inp-height', type='number', min=1.0, max=2.2, step=0.01, value=1.65)
            ], xs=6, md=3),
            dbc.Col([
                dbc.Label("Weight (kg)", className="form-label"),
                dbc.Input(id='inp-weight', type='number', min=30, max=200, step=0.5, value=65)
            ], xs=6, md=3),
        ]),
    ], className="form-section"),

    # Section 2: Dietary Habits
    html.Div([
        html.Div("Dietary Habits", className="form-section-title"),
        dbc.Row([
            dbc.Col([
                dbc.Label("High Caloric Food (FAVC)", className="form-label"),
                dcc.RadioItems(id='inp-favc',
                    options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                    value='yes', inline=True)
            ], xs=6, md=4),
            dbc.Col([
                dbc.Label("Eating Between Meals", className="form-label"),
                make_dropdown('inp-caec', ['no', 'Sometimes', 'Frequently', 'Always'], 'Sometimes')
            ], xs=6, md=4),
            dbc.Col([
                dbc.Label("Alcohol Consumption", className="form-label"),
                make_dropdown('inp-calc', ['no', 'Sometimes', 'Frequently', 'Always'], 'Sometimes')
            ], xs=12, md=4),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Vegetable Consumption (FCVC)", className="form-label"),
                html.Div(dcc.Slider(id='inp-fcvc', min=1, max=3, step=0.5, value=2,
                           marks={1: 'Never', 2: 'Sometimes', 3: 'Always'},
                           tooltip={"placement": "top", "always_visible": False}),
                         style={"paddingBottom": "20px"})
            ], md=4),
            dbc.Col([
                dbc.Label("Meals per Day (NCP)", className="form-label"),
                html.Div(dcc.Slider(id='inp-ncp', min=1, max=4, step=1, value=3,
                           marks={1: '1', 2: '2', 3: '3', 4: '4+'},
                           tooltip={"placement": "top", "always_visible": False}),
                         style={"paddingBottom": "20px"})
            ], md=4),
            dbc.Col([
                dbc.Label("Water Intake (CH2O)", className="form-label"),
                html.Div(dcc.Slider(id='inp-ch2o', min=1, max=3, step=0.5, value=2,
                           marks={1: '<1L', 2: '1-2L', 3: '>2L'},
                           tooltip={"placement": "top", "always_visible": False}),
                         style={"paddingBottom": "20px"})
            ], md=4),
        ]),
    ], className="form-section"),

    # Section 3: Lifestyle
    html.Div([
        html.Div("Lifestyle & Activity", className="form-section-title"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Physical Activity (FAF)", className="form-label"),
                html.Div(dcc.Slider(id='inp-faf', min=0, max=3, step=1, value=1,
                           marks={0: 'None', 1: '1-2 days', 2: '2-4 days', 3: '4-5 days'},
                           tooltip={"placement": "top", "always_visible": False}),
                         style={"paddingBottom": "20px"})
            ], md=4),
            dbc.Col([
                dbc.Label("Screen Time (TUE)", className="form-label"),
                html.Div(dcc.Slider(id='inp-tue', min=0, max=2, step=1, value=1,
                           marks={0: '0-2 hrs', 1: '3-5 hrs', 2: '5+ hrs'},
                           tooltip={"placement": "top", "always_visible": False}),
                         style={"paddingBottom": "20px"})
            ], md=4),
            dbc.Col([
                dbc.Label("Transportation", className="form-label"),
                make_dropdown('inp-mtrans',
                    ['Automobile', 'Motorbike', 'Bike', 'Public_Transportation', 'Walking'],
                    'Public_Transportation')
            ], md=4),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Smoking", className="form-label"),
                dcc.RadioItems(id='inp-smoke',
                    options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                    value='no', inline=True)
            ], md=4),
            dbc.Col([
                dbc.Label("Calorie Monitoring (SCC)", className="form-label"),
                dcc.RadioItems(id='inp-scc',
                    options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                    value='no', inline=True)
            ], md=4),
            dbc.Col([
                dbc.Label("Family History", className="form-label"),
                dcc.RadioItems(id='inp-fh',
                    options=[{'label': ' Yes', 'value': 'yes'}, {'label': ' No', 'value': 'no'}],
                    value='yes', inline=True)
            ], md=4),
        ]),
    ], className="form-section"),

    html.Div([
        dbc.Button("Analyze Risk Profile", id="predict-btn", className="btn-predict mt-3")
    ]),
    html.Div(style={"height": "20px"}),
    html.Div(id='prediction-output'),
], fluid=True)

# ============================================================
# Main Layout
# ============================================================
app.layout = html.Div([
    html.Div([
        html.H1("Childhood Obesity Risk Screening Dashboard",
                className="text-gradient",
                style={"fontSize": "1.6rem", "fontWeight": "700",
                       "textAlign": "center", "padding": "20px 0 16px",
                       "margin": "0", "fontFamily": "Manrope, sans-serif"}),
    ], style={"borderBottom": "1px solid #2A2F45",
              "background": "rgba(15,17,23,0.85)",
              "backdropFilter": "blur(16px)"}),
    dbc.Tabs([
        dbc.Tab(tab1, label="Overview", tab_id="tab-overview",
                label_style={"fontFamily": "Inter, sans-serif"}),
        dbc.Tab(tab2, label="Risk Factor Explorer", tab_id="tab-risk",
                label_style={"fontFamily": "Inter, sans-serif"}),
        dbc.Tab(tab3, label="Model Results", tab_id="tab-models",
                label_style={"fontFamily": "Inter, sans-serif"}),
        dbc.Tab(tab4, label="Cluster Profiles", tab_id="tab-clusters",
                label_style={"fontFamily": "Inter, sans-serif"}),
        dbc.Tab(tab5, label="Screening Tool", tab_id="tab-screening",
                label_style={"fontFamily": "Inter, sans-serif"}),
    ], className="px-3"),
    html.Div([
        html.P("DSC 510 Final Project | Group 2: Rushi Patel, Raffey Akram, Vishnu Doddapaneni | "
               "Prof. Casey Bennett | DePaul University"),
        html.P("This tool is for educational and research purposes only. Not a substitute for medical advice.",
               style={"fontSize": "11px"}),
    ], className="dashboard-footer"),
], className="gradient-bg")

# ============================================================
# Callbacks
# ============================================================
@app.callback(Output('feature-dist-graph', 'figure'), Input('feature-select', 'value'))
def update_feature_dist(feature):
    fig = px.box(df, x='Obesity_Label', y=feature,
                 category_orders={'Obesity_Label': LABEL_ORDER},
                 color='Obesity_Label', color_discrete_map=LABEL_COLORS,
                 title=f'{feature} Distribution by Obesity Level')
    fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=380,
                       xaxis_title="", yaxis_title=feature,
                       xaxis=dict(tickfont=dict(size=11, color="#CBD5E1")))
    return fig

@app.callback(Output('scatter-graph', 'figure'),
              [Input('scatter-x', 'value'), Input('scatter-y', 'value')])
def update_scatter(x_feat, y_feat):
    fig = px.scatter(df, x=x_feat, y=y_feat, color='Obesity_Label',
                     category_orders={'Obesity_Label': LABEL_ORDER},
                     color_discrete_map=LABEL_COLORS,
                     title=f'{x_feat} vs {y_feat}', opacity=0.6)
    fig.update_traces(marker=dict(size=6, line=dict(width=1, color='#141821')))
    fig.update_layout(height=380, legend=dict(font=dict(size=12, color="#CBD5E1")))
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

        age, height, weight = float(age), float(height), float(weight)

        # Encode
        gender_enc = 1 if gender == 'Male' else 0
        fh_enc = 1 if fh == 'yes' else 0
        favc_enc = 1 if favc == 'yes' else 0
        smoke_enc = 1 if smoke == 'yes' else 0
        scc_enc = 1 if scc == 'yes' else 0
        caec_map = {'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3}
        calc_map = {'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3}
        caec_enc, calc_enc = caec_map.get(caec, 1), calc_map.get(calc, 1)
        mtrans_bike = 1 if mtrans == 'Bike' else 0
        mtrans_motorbike = 1 if mtrans == 'Motorbike' else 0
        mtrans_public = 1 if mtrans == 'Public_Transportation' else 0
        mtrans_walking = 1 if mtrans == 'Walking' else 0

        bmi = weight / (height ** 2)
        activity_screen_ratio = faf / (tue + 0.1)
        dietary_risk_score = favc_enc + (3 - fcvc) + caec_enc

        # Classification
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

        # Regression
        reg_dict = {
            'Gender': gender_enc, 'Age': age,
            'family_history_with_overweight': fh_enc, 'FAVC': favc_enc,
            'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec_enc, 'SMOKE': smoke_enc,
            'CH2O': ch2o, 'SCC': scc_enc, 'FAF': faf, 'TUE': tue, 'CALC': calc_enc,
            'MTRANS_Bike': mtrans_bike, 'MTRANS_Motorbike': mtrans_motorbike,
            'MTRANS_Public_Transportation': mtrans_public, 'MTRANS_Walking': mtrans_walking
        }
        reg_features = pd.DataFrame([reg_dict])[feature_names_reg]

        # Clustering
        cluster_dict = {
            'Gender': gender_enc, 'Age': age,
            'family_history_with_overweight': fh_enc, 'FAVC': favc_enc,
            'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec_enc, 'SMOKE': smoke_enc,
            'CH2O': ch2o, 'SCC': scc_enc, 'FAF': faf, 'TUE': tue, 'CALC': calc_enc
        }
        cluster_features = pd.DataFrame([cluster_dict])[feature_names_cluster]

        # Predict
        dt_pred = dt_model.predict(cls_features)[0]
        predicted_class = reverse_label_mapping[dt_pred]
        predicted_bmi = lr_model.predict(scaler_reg.transform(reg_features))[0]
        cluster_pred = km_model.predict(scaler_cluster.transform(cluster_features))[0]
        cluster_name = cluster_names.get(cluster_pred, f"Cluster {cluster_pred}")

        # Risk gauge
        bmi_score = min(max((bmi - 15) / (50 - 15) * 100, 0), 100)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            number={"suffix": "", "font": {"size": 38, "color": "#F1F5F9", "family": "Manrope"},
                     "valueformat": ".1f"},
            title={"text": "BMI Score", "font": {"size": 14, "color": "#94A3B8"}},
            gauge=dict(
                axis=dict(range=[15, 50], tickcolor="#64748B", dtick=5,
                          tickfont=dict(size=10, color="#64748B")),
                bar=dict(color="#3B9AE8", thickness=0.7),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                steps=[
                    dict(range=[15, 18.5], color="rgba(96,165,250,0.15)"),
                    dict(range=[18.5, 25], color="rgba(52,211,153,0.15)"),
                    dict(range=[25, 30], color="rgba(251,191,36,0.15)"),
                    dict(range=[30, 50], color="rgba(248,113,113,0.15)"),
                ],
                threshold=dict(line=dict(color="#F87171", width=3), thickness=0.8, value=bmi),
            ),
        ))
        fig_gauge.update_layout(height=220, margin=dict(t=50, b=10, l=30, r=30),
                                 paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))

        # Recommendations
        recommendations, risk_factors = [], []
        if faf <= 1:
            risk_factors.append("Low physical activity")
            recommendations.append("Increase physical activity to 2-4 days/week")
        if tue >= 2:
            risk_factors.append("High screen time")
            recommendations.append("Reduce screen time to under 3 hours/day")
        if fcvc < 2:
            risk_factors.append("Low vegetable intake")
            recommendations.append("Increase daily vegetable consumption")
        if ch2o < 2:
            risk_factors.append("Low water intake")
            recommendations.append("Drink at least 2 liters of water daily")
        if favc == 'yes':
            risk_factors.append("High-calorie food consumption")
            recommendations.append("Reduce high-calorie food intake")
        if fh == 'yes':
            risk_factors.append("Family history of overweight")
            recommendations.append("Monitor weight closely; focus on preventive habits")
        if not risk_factors:
            risk_factors = ["No major modifiable risk factors identified"]
        if not recommendations:
            recommendations = ["Continue maintaining healthy lifestyle habits"]

        risk_css = RISK_CSS.get(predicted_class, 'risk-moderate')

        result = html.Div([
            # Header
            html.Div([
                html.H4("Prediction Results", style={"margin": "0", "color": "#F1F5F9",
                         "fontFamily": "Manrope, sans-serif", "fontWeight": "700"}),
            ], className="result-header"),

            html.Div([
                # Top row: Risk + Gauge + Cluster
                dbc.Row([
                    dbc.Col([
                        html.Div("Predicted Risk Level",
                                 style={"fontSize": "12px", "color": "#64748B",
                                        "textTransform": "uppercase", "letterSpacing": "1px",
                                        "marginBottom": "12px", "fontWeight": "600"}),
                        html.Div(predicted_class.replace('_', ' '), className=f"risk-badge {risk_css}"),
                    ], md=4, className="text-center", style={"paddingTop": "20px"}),

                    dbc.Col([
                        dcc.Graph(figure=fig_gauge, config=CHART_CONFIG,
                                  style={"height": "220px"})
                    ], md=4),

                    dbc.Col([
                        html.Div("Behavioral Cluster",
                                 style={"fontSize": "12px", "color": "#64748B",
                                        "textTransform": "uppercase", "letterSpacing": "1px",
                                        "marginBottom": "12px", "fontWeight": "600"}),
                        html.Div(cluster_name,
                                 style={"fontSize": "20px", "fontWeight": "700",
                                        "color": "#2DD4BF", "fontFamily": "Manrope"}),
                        html.Div(f"Predicted BMI: {predicted_bmi:.1f} kg/m²",
                                 style={"fontSize": "13px", "color": "#94A3B8", "marginTop": "8px"}),
                        html.Div(f"Actual BMI: {bmi:.1f} kg/m²",
                                 style={"fontSize": "12px", "color": "#64748B"}),
                    ], md=4, className="text-center", style={"paddingTop": "20px"}),
                ], className="mb-4"),

                html.Hr(style={"borderColor": "#2A2F45", "opacity": "0.5"}),

                # Bottom row: Risk Factors + Recommendations
                dbc.Row([
                    dbc.Col([
                        html.Div("Risk Factors",
                                 style={"fontSize": "14px", "fontWeight": "700",
                                        "color": "#F87171", "marginBottom": "12px",
                                        "fontFamily": "Manrope"}),
                        html.Div([
                            html.Div([
                                html.Span("⚠ ", style={"color": "#FBBF24"}),
                                html.Span(rf)
                            ], className="rec-card") for rf in risk_factors[:4]
                        ])
                    ], md=6),
                    dbc.Col([
                        html.Div("Recommendations",
                                 style={"fontSize": "14px", "fontWeight": "700",
                                        "color": "#34D399", "marginBottom": "12px",
                                        "fontFamily": "Manrope"}),
                        html.Div([
                            html.Div([
                                html.Span("✓ ", style={"color": "#34D399"}),
                                html.Span(r)
                            ], className="rec-card") for r in recommendations[:4]
                        ])
                    ], md=6),
                ]),
            ], style={"padding": "24px"}),
        ], className="result-card result-reveal")

        return result

    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


server = app.server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"Starting dashboard on http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
