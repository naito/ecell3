# -*- coding: utf-8 -*-
#
# This is a sample script file of Gauss-Newton
# 

from ecell.ECDDataFile import *

import numpy as np
import os
import sys
import random
import copy
import json


# --------------------------------------------------------
# (0) パラメータ設定
# --------------------------------------------------------

# BEGIN ユーザが設定する値

# m個の時系列fを最もよく近似するn個のパラメータbを見つける。
# ただし、m ≥ n

# ヤコビアンの要素（∂f/∂x）を返すスクリプト
ESS_FILE       = 'osc_session.py'

# カーブデータ（時系列）(関数f f_1~f_m)
# CURVE_DATA_DIR   トレーニングデータを格納するディレクトリ
# CURVE_DATA_DICT  トレーニングデータの辞書
#                  キー：FullPN
#                  値：ECDファイル名
CURVE_DATA_DIR = 'Data'
CURVE_DATA_DICT = {
    'Variable:/:s1:Value' : 'osc_s1.ecd',
    'Variable:/:s2:Value' : 'osc_s2.ecd',
    'Variable:/:s3:Value' : 'osc_s3.ecd' }

# 最適化に用いるデータポイントの設定
# 設定しない場合は、None にする。
T_START    =  0.0       # Noneの場合、先頭のデータから
T_END      = 10.0       # Noneの場合、末尾のデータまで
T_INTERVAL =  0.5       # Noneの場合、すべてのデータポイント

# 最適化するパラメータのFullPNと [ 初期値, 最小値, 最大値 ] (変数x x_1~x_n)
# PARAMETERS  パラメータ情報の辞書
#             キー：FullPN
#             値：初期値
PARAMETERS = { 
    'Process:/:re11:k11' :  0.5,   #  1.0
    'Process:/:re21:k21' : -0.5,   # -1.0
    'Process:/:re32:k32' :  0.5    #  1.0
}

# 最大世代数
MAX_GENERATION   = 100

# 終了条件（充分に小さい残差平方和）
ENOUGH_S = 0.01

# 残差のヤコビアンを求める際のパラメータの差分の割合
DELTA = 0.001


# --------------------------------------------------------
# (1) 関数
# --------------------------------------------------------

def getTargetDataPoints( time_course, t_start = None, t_end = None, interval = None ):
    # ECD時系列データ（numpy.ndarray）または、同じデータ構造のリストから
    # 最適化に用いるデータポイントを抽出して、リストを返す。
    try:
        time_course = time_course.tolist()
    except:
        pass
    
    if t_start == None:
        t_start = time_course[ 0 ][ 0 ]
    if t_end == None:
        t_end = time_course[ -1 ][ 0 ]
    
    # 範囲の前後、範囲内のデータを個別に抽出
    _before = [ d for d in time_course if d[ 0 ] < t_start ]
    _mid    = [ d for d in time_course if d[ 0 ] >= t_start and d[ 0 ] <= t_end ]
    _after  = [ d for d in time_course if d[ 0 ] > t_end ]
    
    # intervalの指定がなければ、範囲内の全データを返して終了。
    if interval == None:
        if len( _mid ):
            return _mid
        else:
            return [[]]
    
    # intervalに沿ってデータを間引く
    # 範囲の前後を削除（範囲外のデータを存在すればそれぞれ１つずつ残す）
    if len( _before ):
        time_course = [ _before[ -1 ]]
    else:
        time_course = []
    
    time_course.extend( _mid )
    
    if len( _after ):
        time_course.append( _after[ 0 ] )
    
    # 間引きの実装
    t = t_start
    reduced_time_cource = []
    
    time_course.reverse()
    while t <= t_end:
        d = time_course.pop()   # 最も時刻の小さいデータ
        while True:
            if t == d[ 0 ]:
                reduced_time_cource.append( [ t, d[ 1 ] ] )
                t += interval
            if len( time_course ) == 0:
                break
            elif t >= d[ 0 ] and t < time_course[ -1 ][ 0 ]:
                reduced_time_cource.append( [ t, d[ 1 ] ] )
                t += interval
            else:
                break
        
        if len( time_course ) == 0:
            break
    
    if len( reduced_time_cource ):
        return reduced_time_cource
    else:
        return [[]]


def calc_next_beta( ess_file, target_data_dict, beta_dict, delta = 0.01, other_files = [] ):
    
    # ess_file         : セッションスクリプトファイル
    # target_data_dict : 最適化対象のデータ辞書
    #                      キー: FullPN
    #                      値  : ECDと同じ形式のリスト（np.arrayではない）
    # beta_dict        : パラメータ辞書
    #                      キー: FullPN
    #                      値  : パラメータの値
    # delta            : 数値計算に用いる∂の比率（デフォルト 0.01）
    # other_files      : ess_fileが必要とする別のファイルのリスト（EMファイルなど）
    
    m = len( target_data_dict ) * target_data_dict[ target_data_dict.keys()[0] ][0]
    n = len( beta_dict )
    parameters = dict( TARGET = target_data_dict, BETA = beta_dict, DELTA = delta, DEL_BETA = None )
    
    # 残差 r を計算する job のID
    r_ID = registerEcellSession( ess_file, parameters, other_files )
    
    # ヤコビアン J の各要素を計算する job のID を格納するリストの初期化（最終的な要素数は n ）
    J_IDs = {}
    for beta_FullPN, beta_value in beta_dict.items():
        parameters['DEL_BETA'] = [ beta_FullPN ]
        J_IDs[ beta_FullPN ] = registerEcellSession( ess_file, parameters, other_files )

    # すべてのjobの終了を待つ。
    run()

    is_JSON_only = True  # シミュレーション結果のファイル内容。0: JSONのみ, 1: JSON以外の情報あり
    residuals_dict = getStdout( r_ID ).strip()
    if residuals_dict.find("\n") > -1:
        is_JSON_only = False
        residuals_dict = json.loads( residuals_dict.split("\n")[ -1 ] )
    else:
        residuals_dict = json.loads( residuals_dict )
    
    # print residuals_dict
    
    del_residuals_dict = {}
    for beta_FullPN, a_job_ID in J_IDs.items():
        if is_JSON_only:
            del_residuals_dict[ beta_FullPN ] = json.loads( getStdout( a_job_ID ) )
        else:
            del_residuals_dict[ beta_FullPN ] = json.loads( getStdout( a_job_ID ).strip().split("\n")[ -1 ] )

    # 最適化対象のデータ y
    # print del_residuals_dict

    y = np.array( target_data_dict.values() )

    # print y

    n_target     = y.shape[0]
    n_time_point = y.shape[1]
    n_y          = n_target * n_time_point

    y = np.reshape( y, ( n_y, 2 ) )
    y = y[ :, 1 : ]

    # print "y"
    # print y

    # 残差 r
    # 辞書のキーの順序が維持されている保証がない（？未確認）ので、
    # 順序が変わっていても正しく動作する実装にしておく。
    f = np.zeros( y.shape )
    # print y.shape
    i = 0
    for a_FullPN in target_data_dict.keys():
        f[ i * n_time_point : (i + 1) * n_time_point, : ] = np.array( residuals_dict[ a_FullPN ] )[ :, 1 : ]
        i += 1

    r = y - f

    # print "r"
    # print r

    # 残差の平方和 S
    S = np.sum( np.square( r ) )

    print "S"
    print S

    # 最適化対象パラメータのベクトル beta
    beta = np.array( [ beta_dict.values() ] )

    # print "beta"
    # print beta

    # ヤコビアン J_r
    # 辞書のキーの順序が維持されている保証がない（？未確認）ので、
    # 順序が変わっていても正しく動作する実装にしておく。
    J_r = np.zeros( ( len( beta_dict ), n_y ) )
    i = 0
    for beta_FullPN, beta_value in beta_dict.items():
        del_b = beta_value * delta
        j = 0
        for a_target_FullPN in target_data_dict.keys():
            J_r[ i, j * n_time_point : (j + 1) * n_time_point ] = np.array( del_residuals_dict[ beta_FullPN ][ a_target_FullPN ] )[ :, 1 ]
            j += 1
        J_r[ i ] = ( f.T - J_r[ i ] ) / del_b
    
        i += 1

    J_r = J_r.T

    # print "J_r"
    # print J_r

    beta_next = np.dot( np.linalg.inv( np.dot( J_r.T, J_r ) ), J_r.T )
    # print "beta_next (1):  {}".format( beta_next.shape )
    # print "beta_next (1):"
    # print beta_next
    beta_next = np.dot( beta_next, r )
    # print "beta_next (2):  {}".format( beta_next.shape )
    # print "beta_next (2):"
    # print beta_next
    beta_next = beta.T - beta_next
    # print "beta_next (3):  {}".format( beta_next.shape )
    # print "beta_next (3):"
    # print beta_next

    # beta_next = beta - np.dot( np.dot( np.linalg.inv( np.dot( J_r.T, J_r ) ), J_r.T ), beta )

    beta_next_dict = copy.deepcopy( beta_dict )

    for a_beta_FullPN, a_beta_next_value in zip( beta_dict.keys(), beta_next.reshape((beta_next.shape[0],)).tolist() ):
        beta_next_dict[ a_beta_FullPN ] = a_beta_next_value

    # print "beta_next:\n{}".format( beta_next_dict )

    # sys.exit()

    return S, beta_next_dict


# --------------------------------------------------------
# (2) データの準備
# --------------------------------------------------------

# 現時点のパラメータを格納する変数 beta を初期化
beta_dict = copy.deepcopy( PARAMETERS )

# theFullPNs  残差のヤコビアンを構成する関数（f）と変数（b）のFullPNを格納する辞書
theFullPNs = dict( f = CURVE_DATA_DICT.keys(), b = PARAMETERS.keys() )

# J_r  残差のヤコビアン（m×n行列、全要素ゼロで初期化）
J_r      = np.zeros(( len( theFullPNs['f'] ), len( theFullPNs['b'] )))
J_r_next = copy.deepcopy( J_r )

# βの現在値のリスト
p = []
for b in theFullPNs['b']:
    p.append( PARAMETERS[ b ] )

# トレーニングデータを格納した辞書
target_data_dict = {}

for FullPN, ECDFileName in CURVE_DATA_DICT.items():
    aTimeCouse = ECDDataFile()
    aTimeCouse.load( os.sep.join(( CURVE_DATA_DIR.rstrip( os.sep ), ECDFileName )) )
    target_data_dict[ FullPN ] = getTargetDataPoints( aTimeCouse.getData(), T_START, T_END, T_INTERVAL )

"""
for FullPN, tc in target_data_dict.items():
    print "\n" + FullPN
    for dp in tc:
        print "{} : {}".format( dp[0], dp[1] )
"""

# --------------------------------------------------------
# (3) 反復計算
# --------------------------------------------------------

for i in range( MAX_GENERATION ):
    
    # 現ラウンドの残差平方和 S と、次ラウンドのパラメータセットβ(S+1)（beta_dict_next）を算出
    S, beta_dict_next = calc_next_beta( ESS_FILE, target_data_dict, beta_dict, DELTA )
    
    if S <= ENOUGH_S:
        break
    else:
        beta_dict = beta_dict_next


# --------------------------------------------------------
# (4) 結果出力
# --------------------------------------------------------

for FullPN, p in beta_dict_next.items():
    print "{} : {}".format( FullPN, p )
