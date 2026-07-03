import sys
import json
import fitz
from datetime import datetime

UNIDADES = ["", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
DIEZ_A_DIECINUEVE = ["DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"]
DECENAS = ["", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
CENTENAS = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]

def _tres_cifras(n):
    if n == 0:
        return ""
    if n == 100:
        return "CIEN"
    c, resto = divmod(n, 100)
    partes = []
    if c:
        partes.append(CENTENAS[c])
    if resto:
        if resto < 10:
            partes.append(UNIDADES[resto])
        elif resto < 20:
            partes.append(DIEZ_A_DIECINUEVE[resto - 10])
        else:
            d, u = divmod(resto, 10)
            if d == 2 and u > 0:
                partes.append("VEINTI" + UNIDADES[u].lower().upper())
            else:
                if u:
                    partes.append(DECENAS[d] + " Y " + UNIDADES[u])
                else:
                    partes.append(DECENAS[d])
    return " ".join(partes)

def numero_a_letras(n):
    n = int(n)
    if n == 0:
        return "CERO"
    if n == 1:
        return "UN"
    partes = []
    millones, resto = divmod(n, 1000000)
    miles, resto = divmod(resto, 1000)
    if millones:
        if millones == 1:
            partes.append("UN MILLON")
        else:
            partes.append(_tres_cifras(millones) + " MILLONES")
    if miles:
        if miles == 1:
            partes.append("MIL")
        else:
            partes.append(_tres_cifras(miles) + " MIL")
    if resto:
        partes.append(_tres_cifras(resto))
    return " ".join(partes)

def formatar_import(amount_raw):
    s = str(amount_raw).strip().replace('€', '').replace(' ', '')
    s = s.replace('.', '').replace(',', '.') if (',' in s and '.' in s) else s.replace(',', '.')
    value = round(float(s), 2)
    enters = int(value)
    centims = round((value - enters) * 100)
    cifras = f"{enters:,}".replace(',', '.') + f",{centims:02d}"
    if centims:
        letras = f"{numero_a_letras(enters)} CON {centims:02d}/100"
    else:
        letras = numero_a_letras(enters)
    return cifras, letras

def fill(input_path, output_path, data):
    doc = fitz.open(input_path)
    page = doc[0]
    values = {
        'ApellidosRow1': data.get('cognoms', ''),
        'NIFRow1': data.get('nif', ''),
        'Nombre Row1': data.get('nom', ''),
        'Número de Cuenta de ValoresRow1': data.get('gvc_account_number', ''),
        '3FECHA Y HORA DE RECEPCIÓN DE LA ORDEN DE APORTACIÓN': data.get('fecha_hora', ''),
    }

    cifras, letras = formatar_import(data.get('recurring_amount', '0'))
    values['IMPORTE APORTACIÓN EN CIFRAS'] = cifras
    values['IMPORTE APORTACIÓN EN LETRAS'] = letras

    if data.get('es_menor_o_empresa'):
        values['ApellidosRow1_2'] = data.get('representant_cognoms', '')
        values['NIFRow1_2'] = data.get('representant_nif', '')
        values['NombreRow1'] = data.get('representant_nom', '')
        values['En calidad de Apoderado solidariomancomunado Administrador Tutor legal Row1'] = data.get('representant_qualitat', '')

    for widget in page.widgets():
        name = widget.field_name
        if name in values:
            widget.field_value = values[name]
            widget.update()

    doc.save(output_path)
    doc.close()

if __name__ == '__main__':
    data = json.loads(sys.argv[3])
    fill(sys.argv[1], sys.argv[2], data)
    print("OK")
