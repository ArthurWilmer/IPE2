from abstra.forms import *
from abstra.tables import run, insert, update_by_id
from datetime import datetime
from abstra.forms import display_image

display_image(
    "https://i.postimg.cc/3w8Qk3xP/midas-png.png",
    subtitle="",
)
auth_info = get_user()
email = auth_info.email

if not '@ime.eb.br' in email:
    display('e-mail inválido!')
    exit()


def list_investors():
    sql = """
        SELECT id, email, name FROM remax;
    """
    return run(sql)


def get_investor_data(investor_id):
    sql = """
        SELECT email, name, tempo_uso_campo, precisa_manut, data_da_ultima_manut, data_prox_manut, 	data_de_fabricacao
        FROM remax
        WHERE id = $1;
    """
    params = [investor_id]
    return run(sql, params)[0]


def preprocessing_date(date):
    if date != None:
        date = datetime(date.year, date.month, date.day)
        date = date.replace(tzinfo=None)
        date = date.strftime("%Y/%m/%d, %H:%M:%S")
    return date


registration = (
    read_multiple_choice(
        "Olá! O que gostaria de fazer?",
        [
            {"label": "Registrar uma nova peça!", "value": "first_time"},
            {"label": "Atualizar informações de uma peça já cadastrada!",
                "value": "update"},
        ],
    )
)

if registration == "first_time":
    investor = (
        Page()
        .read("Nome da peça", key="P_name")
        .read_number("Tempo de uso em campo ( em horas e número inteiro!)", key="Usage_time")
        .read_email("E-mail do último responsável", key="email")
        .read_multiple_choice(
            "A peça já passou da data de Manutenção? ",
            [
                {"label": "Sim", "value": "yes"},
                {"label": "Não", "value": "no"},
            ],
            key="Expired_Bool"
        )
        .read_date("Data da última manutenção", key="Last_manu")
        .read_date("Data da próxima manutenção", key="Next_manu")
        .read_date("Data de fabricação", key="Fabrication_date")
        .run("Cadastrar!")
    )

    (name, tempo_campo, email, from_us, manut_date,
     next_manut_date, signature_date) = investor.values()

    signature_date = preprocessing_date(signature_date)
    manut_date = preprocessing_date(manut_date)
    next_manut_date = preprocessing_date(next_manut_date)
    insert("remax", {"email": email, "name": name, "tempo_uso_campo": tempo_campo,
           "precisa_manut": from_us, "data_da_ultima_manut": manut_date, "data_prox_manut": next_manut_date})
    # add_investor(email=email, name=name, from_us=from_us, signature_date=signature_date)
    display(f"Nome da peça: {name}\nTempo de uso total: {tempo_campo}\nEmail: {email}\nPossui data de manutenção ?:{from_us}\nData da última manutenção: {manut_date}\nData da próxima manutenção: {next_manut_date}\nData de fabricação: {signature_date}")
    display("Nova peça cadastrada! Obrigado!")

else:
    investors_database = list_investors()

    investor_dict = [
        {"label": f'{investor_dict["name"]} ({investor_dict["email"]})',
         "value": investor_dict["id"]}
        for investor_dict in investors_database
    ]

    investor_id = read_dropdown(
        "Qual peça você gostaria de atualizar?", investor_dict
    )

    investor_dict = get_investor_data(investor_id)

    updated_investor = (
        Page()
        .read("name", required=False, key="name2")
        .read_email("email", required=False, key="email2")
        .read_number("Tempo de uso em campo", key="tempo2")
        .read_multiple_choice(
            "A peça já passou da data de Manutenção? ",
            [
                {"label": "Sim", "value": "yes"},
                {"label": "Não", "value": "no"},
            ],
            key="Expired_Bool"
        )
        .read_date("Data da última manutenção", key="Last_manu")
        .read_date("Data da próxima manutenção", key="Next_manu")
        .run("Send")
    )
    (name2, email2, tempo2, Expired_Bool, Last_manu, Next_manu) = updated_investor.values()
    update_id = update_by_id("remax", investor_id, {
                 "name": name2 or investor_dict["name"], "email": email2 or investor_dict["email"], "tempo_uso_campo": tempo2+investor_dict["tempo_uso_campo"]})
    print(update_id[0]['name'])
    display(f"Nome da peça: {name2}\nTempo de uso adicionado: {tempo2}\nEmail: {email2}\nPossui data de manutenção ?:{Expired_Bool}\nData da última manutenção: {Last_manu}\nData da próxima manutenção: {Next_manu}")
    display("Informações da peça atualizada! Até a próxima.")