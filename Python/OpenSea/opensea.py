
import os
import json
import tabulate
from selenium import webdriver
from selenium.webdriver.common.by import By

from dotenv import load_dotenv
load_dotenv()

# retrieve chrome driver path
# obtener ruta de arvhivo del chrome driver
DriverPath = str(os.getenv("DRIVER_PATH"))
# retrieve opensea rankings url
# obtener el url del sitio opensea rankings 
OpenSeaRankingsUrl = str(os.getenv("OPENSEA_RANKINGS_URL"))

# patterns to specify start and end points for regex
# patrones para usar regex con la pagina de opensea
EndPattern = '],"pageInfo"'
StartPattern = '{"edges":['
# selector for next button if necessary
# el codigo para el boton 'next' si es necesario
NextButtonSelector = "//button/i[contains(text(), 'arrow_forward_ios')]"

# this function will scrape the specified number of pages from the rankings site
# este funcion obtiene la information del sitio opensea por el numero de paginas especificado
def scrapeRankings(numPages=1):
    # webdriver options for background run
    # opciones por el webdriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.headless = True
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
    driver = webdriver.Chrome(options=options, executable_path=DriverPath)
    # get opensea rankings url
    # obtiene la pagina de rankings
    driver.get(OpenSeaRankingsUrl)

    # get button element, assumed to exist on first page
    # obtiene el boton 'next' para la primera pagina
    nextButton = driver.find_element(By.XPATH, NextButtonSelector)
    # counter for page count
    # contador para las paginas
    pageCount = 1
    # this will loop until the next button is not found or page limit reached
    # esto sigue hasta que no puede encontrar el boton 'next' o ha llegado al limite de paginas
    outputHtml = ""
    while(nextButton is not None and pageCount<=numPages):
        print("scraping page: " + str(pageCount) + "...")
        # click the button
        # clic en el boton
        nextButton.click()
        
        # get the page html and trim to an array, ie [{node...}, {node...}]
        # obtiene la pagina en html y lo corta, ie [{node...}, {node...}]
        html =  driver.page_source
        cleanHtml = html[html.find(StartPattern)+len(StartPattern)-1:html.find(EndPattern)+1]
        
        # if greater than page 1, format to append
        # si la cuenta de pagina es mas que 1, formatear para añadir
        if(pageCount > 1):
            outputHtml = outputHtml[:-1]
            cleanHtml = "," + cleanHtml[1:]
        outputHtml += cleanHtml

        # look for next button
        # busca por el boton 'next'
        try:
            nextButton = driver.find_element(By.XPATH, NextButtonSelector)
        except:
            nextButton = None
        pageCount += 1
    # return html
    # devolver el html
    return outputHtml

def collectionObjectToTable(collectionObjects, numResults):
    # table header
    # encabezados del data
    data = [[
        "name",
        "slug",
        "floorPrice",
        "numOwners",
        "totalSupply",
        "totalVolume"]]

    # loop through each collection object
    # recorrer cada objeto de la colección
    for i in range(0, len(collectionObjects)):
        # break if result count met
        # interrumpir si se cumple el recuento de resultados
        if((i+1) >= numResults):
            break
        collection = collectionObjects[i]["node"]
        
        # build new row
        # construir nueva fila
        newRow = []
        newRow.append(collection["name"])
        newRow.append(collection["slug"])
        # check if floor price is null
        # verificar si el precio mínimo es nulo
        if(collection["statsV2"]["floorPrice"] == None):
            newRow.append("None")
        else:
            newRow.append(collection["statsV2"]["floorPrice"]["unit"])
        newRow.append(collection["statsV2"]["numOwners"])
        newRow.append(collection["statsV2"]["totalSupply"])
        newRow.append(collection["statsV2"]["totalVolume"]["unit"])

        # add new row
        # añadir nueva fila
        data.append(newRow)
    # return collection table
    # devolver los datos
    return data
    
def getOpenSeaCollections(numResults=100, printToConsole=False):
    # get number of pages to scrape
    # obtener el número de páginas para raspar
    pagesToScrape = int(numResults/100) + 1
    # get html for all pages
    # obtener html para todas las páginas
    collectionHtml = scrapeRankings(pagesToScrape)
    # convert clean html to json objects
    # convertir html a objetos json
    collectionsJson = json.loads(collectionHtml)
    # convert json objects to 2d array
    # convertir objetos json a matriz 2d
    collectionData = collectionObjectToTable(collectionsJson, numResults)
    # print table if necessary
    # mostrar tabla si es necesario
    if(printToConsole):
        tableString = tabulate.tabulate(
            collectionData,
            tablefmt="plain",
            numalign="right",
            stralign="left"
        )
        print(tableString)
    # return collection table
    # devolver los datos
    return collectionData