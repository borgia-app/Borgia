from django.http import HttpResponse
import xlsxwriter
import json


def worksheet_write_line(workbook, worksheet, data, bold=False, init_column=0,
                         init_row=0):
    """
    Ecrit dans worksheet une ligne par i dans data.
    Par exemple :
    data = [[user1, 1], [user2, 2]]
    Ecrit deux lignes [user1, 1] et [user2, 2] dans deux colonnes.
    Procède à l'autofit
    :param workbook: class workboot de xlsxwriter
    :param data: liste de lignes
    :param worksheet: class worksheet de xlsxwriter
    :param bold: Si vrai, les lignes sont en gras
    :param init_column: index où commencer à écrire
    :param init_row: index où commencer à écrire
    """

    col = init_column
    row = init_row
    max_width = [len('Nom Prénom'), len('Bucque'), len('Username'),
                 len('Pondération')]

    for line in data:
        # Ecriture de la ligne
        worksheet.write_row(row, col, line, workbook.add_format(
            {'bold': bold}))
        row += 1
        # Recherche de la taille max pour autofit
        for i, c in enumerate(line):
            try:
                if len(str(c)) > max_width[i]:
                    max_width[i] = len(str(c))
            except TypeError:
                #  Cas où ce n'est pas un élément convertissable en string
                pass

    # Application de l'autofit
    for i in range(0, len(max_width)):
        worksheet.set_column(i, i, max_width[i]+2)


def workboot_init(workbook_name, macro=None, button_caption=None):
    """
    Initialise le fichier Excel, avec ou sans macro (une macro max)
    :param workbook_name: string, nom à appliquer au fichier xl
    :param macro: string, nom de la macro à appliquer
    :param button_caption, string, valeur du bouton à lier à la macro
    :return workbook, worksheet
    """

    # Cas où une macro est ajouté, fichier xlxm
    if macro is not None:
        response = HttpResponse(content_type='text/xlsm')
        response['Content-Disposition'] = ('attachment; filename="'
                                           + workbook_name + '.xlsm"')
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        # Stocké dans la RAM
        workbook.add_vba_project('vbaProject.bin')
        # Ajout de la macro
        worksheet = workbook.add_worksheet()
        print(len(button_caption))
        worksheet.insert_button('F3', {'macro': macro,
                                       'caption': button_caption,
                                       'width': len(button_caption)*10,
                                       'height': 30})
    # Cas où pas de macro, fichier xlsx
    else:
        response = HttpResponse(content_type='text/xlsx')
        response['Content-Disposition'] = ('attachment; filename="'
                                           + workbook_name + '.xlsx"')
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        # Stocké dans la RAM
        worksheet = workbook.add_worksheet()

    # Set des noms du workbook et de la sheet
    # Doit être les mêmes que sur la macro, s'il y en a une.
    # Permet d'éviter les problèmes des différentes versions.
    workbook.set_vba_name('ThisWorkbook')
    worksheet.set_vba_name('Feuil1')

    return workbook, worksheet, response


def list_base_ponderation_from_file(f):

    # Traitement sur le string pour le convertir en liste identifiable json
    initial = str(f.read())
    data_string = initial[2:len(initial)]
    data_string = data_string[0:len(data_string)-1]
    data_string = data_string.replace('\\n', '')

    # Gestion des erreurs si le fichier contient du blanc après les données
    data_string = data_string[0:data_string.rfind(']')+1]

    # Conversion json
    data = json.loads(data_string)

    # Lecture json
    list_base = []
    list_ponderation = []
    for dual in data:
        list_base.append(dual[0])
        list_ponderation.append(dual[1])
    return list_base, list_ponderation


def list_user_ponderation_errors_from_list(f, token):

    if token == 'True':
        token = True
    else:
        token = False

    list_base_ponderation = list_base_ponderation_from_file(f)

    list_user = []
    list_ponderation = []
    list_error = []

    for i, b in enumerate(list_base_ponderation[0]):

        # Si le fichier contient des numéros de jetons
        if token is True:
            try:
                list_user.append(User.objects.get(token_id=b))
                list_ponderation.append(list_base_ponderation[1][i])
            except ObjectDoesNotExist:
                list_error.append([b, list_base_ponderation[1][i]])

        # Si le fichier contient des usernames
        else:
            try:
                list_user.append(User.objects.get(username=b))
                list_ponderation.append(list_base_ponderation[1][i])
            except ObjectDoesNotExist:
                list_error.append([b, list_base_ponderation[1][i]])

    return list_user, list_ponderation, list_error, list_base_ponderation
