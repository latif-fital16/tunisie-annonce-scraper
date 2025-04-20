import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Charger les données depuis le fichier CSV généré par la Partie 1
try:
    df = pd.read_csv("annonces_tayara_jan_fev_2025.csv")
except FileNotFoundError:
    print("Fichier annonces_tayara_jan_fev_2025.csv non trouvé. Assurez-vous que le scraping de la Partie 1 a été exécuté.")
    df = pd.DataFrame()  # DataFrame vide si le fichier n'existe pas

# Si le DataFrame est vide, afficher un message
if df.empty:
    print("Aucune donnée disponible pour afficher dans le tableau de bord.")
    annonces_data = []
else:
    # Ajouter une colonne pour le mois (pour le filtrage)
    df["month"] = df["date_publication"].apply(lambda x: x.split("/")[1] if x != "N/A" else "N/A")
    annonces_data = df.to_dict("records")

# Créer l'application Dash
app = dash.Dash(__name__)

# Liste des localisations et mois pour les filtres
localisations = sorted(df["localisation"].unique()) if not df.empty else []
mois = sorted(df["month"].unique()) if not df.empty else ["01", "02"]

# Mise en page du tableau de bord
app.layout = html.Div([
    html.H1("Tableau de bord des annonces immobilières (Janvier/Février 2025)", style={"textAlign": "center"}),
    
    # Filtres
    html.Div([
        html.Label("Filtrer par localisation :"),
        dcc.Dropdown(
            id="localisation-filter",
            options=[{"label": loc, "value": loc} for loc in localisations],
            value=None,
            placeholder="Sélectionnez une localisation",
            style={"width": "50%"}
        ),
    ], style={"margin": "20px"}),
    
    html.Div([
        html.Label("Filtrer par mois :"),
        dcc.Dropdown(
            id="month-filter",
            options=[{"label": f"Mois {m}", "value": m} for m in mois],
            value=None,
            placeholder="Sélectionnez un mois",
            style={"width": "50%"}
        ),
    ], style={"margin": "20px"}),
    
    # Tableau des annonces
    html.H2("Liste des annonces"),
    dash_table.DataTable(
        id="annonces-table",
        columns=[
            {"name": "Titre", "id": "titre"},
            {"name": "Prix", "id": "prix"},
            {"name": "Type de bien", "id": "type_bien"},
            {"name": "Localisation", "id": "localisation"},
            {"name": "Superficie", "id": "superficie"},
            {"name": "Date de publication", "id": "date_publication"},
            {"name": "Lien", "id": "lien", "type": "text", "presentation": "markdown"}
        ],
        data=annonces_data,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "5px"},
        style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"}
    ),
    
    # Visualisation
    html.H2("Répartition des prix par localisation"),
    dcc.Graph(id="price-histogram")
])

# Callback pour mettre à jour le tableau et le graphique en fonction des filtres
@app.callback(
    [Output("annonces-table", "data"),
     Output("price-histogram", "figure")],
    [Input("localisation-filter", "value"),
     Input("month-filter", "value")]
)
def update_dashboard(localisation, month):
    # Filtrer les données
    filtered_df = df
    if localisation:
        filtered_df = filtered_df[filtered_df["localisation"] == localisation]
    if month:
        filtered_df = filtered_df[filtered_df["month"] == month]
    
    # Préparer les données pour le tableau
    table_data = filtered_df.to_dict("records")
    
    # Créer un histogramme des prix par localisation
    if not filtered_df.empty:
        fig = px.histogram(
            filtered_df,
            x="prix",
            color="localisation",
            title="Répartition des prix par localisation",
            labels={"prix": "Prix (TND)", "localisation": "Localisation"}
        )
    else:
        fig = px.histogram(title="Aucune donnée disponible")
    
    return table_data, fig

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True, port=8050)  # Changement ici : run_server -> run