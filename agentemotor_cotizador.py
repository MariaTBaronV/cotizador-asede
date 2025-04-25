from playwright.sync_api import sync_playwright

def cotizar_seguro(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Ir a la página de Agentemotor
        page.goto("https://proaseguros.co.agentemotor.com/")

        if data.get("placa"):
            # Búsqueda por Placa
            page.fill('#plate', data['placa'])
            page.click('#btn-plate')
            page.wait_for_selector('.card-vehicle')
            page.click('text=Es mi vehículo')
        else:
            # Búsqueda por referencia (falta implementarlo luego si quieres)
            return "Actualmente solo soportamos búsqueda por placa."

        # Llenar datos adicionales del vehículo
        page.click('#plate_type')
        page.get_by_text('Particular').click()

        page.click('#use_type')
        page.get_by_text(data['tipo_uso']).click()

        page.fill('#accesories_price', str(data['accesorios']))

        page.fill('#ubication', data['municipio'])
        page.click('text=Siguiente')

        # Llenar datos del propietario
        page.click('#identification_type')
        page.get_by_text('Cédula de ciudadania').click()

        page.fill('#identification_number', data['documento'])
        page.fill('#first_name', data['nombres'])
        page.fill('#last_name', data['apellidos'])
        page.fill('#birth_date', data['fecha_nacimiento'])  # Formato YYYY-MM-DD

        # Género
        page.check(f'input[value="{data["genero"]}"]')  # "M" o "F"

        page.click('#occupation')
        page.get_by_text(data['ocupacion']).click()

        page.click('#marital_status')
        page.get_by_text(data['estado_civil']).click()

        page.fill('#phone', data['telefono'])
        page.fill('#email', data['correo'])

        # Aceptar términos
        page.check('#agree_terms')

        # Aquí no automatizamos el reCAPTCHA (lo hace el usuario)

        browser.close()
        return "Cotización preparada. Por favor finaliza el reCAPTCHA manualmente."

