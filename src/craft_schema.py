from src.modules.fetch_config import fetch_prims
from src.modules.parser import parse_ids

def main():

    prims, df_prim_cyp, df_lat_cyp = fetch_prims()

    df_prim_cyp = df_prim_cyp.explode('cyp').reset_index(drop=True)
    df_lat_cyp['cyp'] = df_lat_cyp['cyp'].copy().apply(parse_ids)
    df_lat_cyp = df_lat_cyp.explode('cyp').reset_index(drop=True)

    # xform/(?<=[a-z])e/E/
    df_prim_cyp['exp'] = '- xform/' + df_prim_cyp['elms'] + '/' + df_prim_cyp['cyp']
    df_lat_cyp['exp'] = '- xform/' + df_lat_cyp['cyp'] + '/' + df_lat_cyp['lat']
    df_lat_cyp['exp2'] = '- xform/' + df_lat_cyp['lat'] + '/' + df_lat_cyp['cyp']

    for serie in [df_prim_cyp['exp'], df_lat_cyp['exp'], df_lat_cyp['exp2']]:
        print('\n'.join(serie.to_list()))
        print('\n\n\n')