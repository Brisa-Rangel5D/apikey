from flask import Flask, render_template, request
import requests

app = Flask(__name__)


API_KEY = "M5NhHaDzZX29xj3FjzLWgH4hbhBjE9hd1uK8W8vm"

ENDPOINT = "https://api.nal.usda.gov/fdc/v1/foods/search"


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/resultado", methods=["POST"])
def resultado():
    alimento = request.form["alimento"]

  
    parametros = {
        "api_key": API_KEY,
        "query": alimento,
        "dataType": ["Branded", "Survey (FNDDS)", "Foundation", "SR Legacy"],
        "pageSize": 1
    }

   
    try:
        respuesta = requests.get(ENDPOINT, params=parametros)
    except:
        return render_template("resultado.html", nombre=alimento,
                               error="No se pudo conectar con la API del USDA.")

  
    if respuesta.status_code != 200:
        return render_template(
            "resultado.html",
            nombre=alimento,
            error=f"Error {respuesta.status_code}: {respuesta.text}"
        )

    datos = respuesta.json()


    if "foods" not in datos or len(datos["foods"]) == 0:
        return render_template("resultado.html", nombre=alimento, error="No se encontraron alimentos.")

    alimento_info = datos["foods"][0]

    lista_nutrientes = []

    if "foodNutrients" in alimento_info:
        lista_nutrientes = alimento_info["foodNutrients"]

    if "foodNutrientsList" in alimento_info and len(lista_nutrientes) == 0:
        lista_nutrientes = alimento_info["foodNutrientsList"]

    nutrientes = {n.get("nutrientName", ""): n.get("value", "No disponible") for n in lista_nutrientes}

    
    calorias = nutrientes.get("Energy",
               nutrientes.get("Energy (Atwater General Factors)", "No disponible"))

    proteina = nutrientes.get("Protein", "No disponible")

    carbohidratos = nutrientes.get("Carbohydrate, by difference",
                     nutrientes.get("Carbohydrate", "No disponible"))

    grasa = nutrientes.get("Total lipid (fat)",
             nutrientes.get("Total Fat", "No disponible"))

    
    try:
        p = float(proteina)
        c = float(carbohidratos)
        g = float(grasa)

        if p > c and p > g:
            clasificacion = "Este alimento es principalmente PROTEÍNA."
        elif c > p and c > g:
            clasificacion = "Este alimento es principalmente CARBOHIDRATOS."
        elif g > p and g > c:
            clasificacion = "Este alimento es principalmente GRASAS."
        else:
            clasificacion = "Este alimento tiene una composición equilibrada."

    except:
        clasificacion = "No hay suficiente información para clasificar este alimento."

  
    return render_template(
        "resultado.html",
        nombre=alimento,
        calorias=calorias,
        proteina=proteina,
        carbohidratos=carbohidratos,
        grasa=grasa,
        clasificacion=clasificacion
    )


if __name__ == "__main__":
    app.run(debug=True)