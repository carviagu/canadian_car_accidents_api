###############################################
# Script para el preprocesado de los datos
# para que puedan ser consumidos por el modelo.
###############################################


# Columnas
acc_columns = ['C_MNTH', 'C_WDAY', 'C_HOUR','C_VEHS', 'C_CONF', 
               'C_RCFG', 'C_WTHR', 'C_RSUR', 
               'C_RALN', 'C_TRAF', 'C_PERS']

model_columns = ['C_MNTH', 'C_WDAY', 'C_VEHS', 'C_RCFG', 'C_WTHR', 'C_RSUR', 'C_RALN',
                'C_TRAF', 'C_PERS', 'C_HOUR_A', 'C_HOUR_M', 'C_CONF_O',
                'C_CONF_TO', 'C_CONF_TS']

# main
def preprocess(data = None):

    data = data[acc_columns]
    # Reduce categories
    data = category_reduction(data)
    # Missing 
    data = missing(data)
    # Encoding
    data = encode(data)
    # Final data
    data = data[model_columns]

    return data


def clean_data(data = None):

    # Eliminamos filas duplicadas
    data.drop_duplicates(keep='last', inplace=True)

    # Agregación
    data = data.groupby(acc_columns).agg(C_PERS=('P_USER', 'count')).reset_index()

    return data

def category_reduction(data = None):

    # Diccionario con los datos de reducciones
    variables = {
        'C_HOUR' : {
            'night' : ['20', '21', '22', '23', '00', '01', '02', '03', '04', '05', '06'],
            'morning' : ['07', '08', '09', '10', '11', '12', '13'],
            'afternoon' : ['14', '15', '16', '17', '18', '19']
        },
        'C_CONF' : {
            'one vehicle' : ['01', '02', '03', '04', '05', '06'],
            'two same dir' : ['21', '22', '23', '24', '25'],
            'two opp dir' : ['31', '32', '33', '34', '35', '36', '41']
        },
        'C_RCFG' : {
            'normal' : ['01'],
            'specific' : ['02', '03', '04', '05', '06', '07', '08', '09', '10']
        },
        'C_WTHR' : {
            'normal' : ['1'],
            'bad' : ['3', '2', '4', '5', '6', '7']
        },
        'C_RSUR' : {
            'normal' : ['1', '2'],
            'dragged' : ['3', '4', '5', '6', '7', '8', '9']
        },
        'C_RALN' : {
            'normal' : ['1'],
            'curve/ramp' : ['2', '3', '4', '5', '6']
        },
        'C_TRAF' : {
            'safe' : ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            'unsafe' : ['18']
        },
        'C_MNTH' : {
            'oto/inv' : ['10', '11', '12', '01', '02', '03'],
            'prim/ver' : ['04', '05', '06', '07', '08', '09']
        },
        'C_WDAY' : {
            'week' : ['1', '2', '3', '4'],
            'weekend' : ['5', '6', '7']
        }
    }

    for val in variables:
        for cat in variables[val]:
            data[val] = data[val].replace(to_replace = variables[val][cat], value = cat)
    
    return data

def missing(data = None):

    especial_values = [['Q', 'QQ', 'QQQQ'], ['U', 'UU', 'UUUU']]

    values = {
        'C_HOUR' : ['night', 'night'],
        'C_CONF' : ['one vehicle', 'one vehicle'],
        'C_RCFG' : ['specific', 'normal'],
        'C_WTHR' : ['bad', 'normal'],
        'C_RSUR' : ['dragged', 'dragged'],
        'C_RALN' : ['curve/ramp', 'normal'],
        'C_TRAF' : ['safe', 'safe']
    }

    for value in values:
        i = 0
        for especial in especial_values:
            data[value] = data[value].replace(to_replace=especial, value = values[value][i])
            i = i + 1

    return data


def encode(data = None):
    
    # Numeric
    numeric = ['C_VEHS', 'C_PERS']
    for col in numeric:
        data[col] = data[col].astype(float)

    # LabelEncoder
    labelCat = {
        'C_RCFG': {'normal': 0, 'specific': 1},
        'C_WTHR': {'bad': 0, 'normal': 1},
        'C_RSUR': {'dragged': 0, 'normal': 1},
        'C_RALN': {'curve/ramp': 0, 'normal':1},
        'C_TRAF': {'safe': 0, 'unsafe': 1},
        'C_MNTH': {'oto/inv': 0, 'prim/ver': 1}, 
        'C_WDAY': {'week': 0, 'weekend': 1}
    }

    for cat in labelCat:
        data[cat] = data[cat].replace(labelCat[cat])

    # OneHotEncoder
    oneCat1 = {
        'C_HOUR_A': {'night': 0, 'morning': 0, 'afternoon': 1},
        'C_HOUR_M': {'night': 0, 'morning': 1, 'afternoon': 0},
        'C_HOUR_N': {'night': 1, 'morning': 0, 'afternoon': 0}
    }
    oneCat2 = {
        'C_CONF_O': {'one vehicle': 1, 'two same dir': 0, 'two opp dir': 0},
        'C_CONF_TO': {'one vehicle': 0, 'two same dir': 0, 'two opp dir': 1},
        'C_CONF_TS': {'one vehicle': 0, 'two same dir': 1, 'two opp dir': 0}
    }

    for cat in oneCat1:
       data[cat] = data['C_HOUR'].replace(oneCat1[cat])
    
    for cat in oneCat2:
       data[cat] = data['C_CONF'].replace(oneCat2[cat])

    data = data.drop(['C_HOUR', 'C_CONF'], axis=1)

    return data

