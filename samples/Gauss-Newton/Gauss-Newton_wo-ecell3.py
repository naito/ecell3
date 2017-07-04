# -*- coding: utf-8 -*-
#
# This is a sample script file of Gauss-Newton without E-Cell3
# 

from ecell.ECDDataFile import *

import numpy as np
import os
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
ESS_FILE       = 'calc_residual.py'

# カーブデータ（時系列）(関数f f_1~f_m)
# CURVE_DATA_DIR   トレーニングデータを格納するディレクトリ
# CURVE_DATA_DICT  トレーニングデータの辞書
#                  キー：FullPN
#                  値：ECDファイル名
CURVE_DATA_DIR = 'Data'
CURVE_DATA_DICT = {
    'Variable:/:S:Value' : 'S.ecd',
    'Variable:/:P:Value' : 'P.ecd' }

# 最適化に用いるデータポイントの設定
# 設定しない場合は、None にする。
T_START    = 0.0         # Noneの場合、先頭のデータから
T_END      = 900.0       # Noneの場合、末尾のデータまで
T_INTERVAL = 100.0       # Noneの場合、すべてのデータポイント

# 最適化するパラメータのFullPNと [ 初期値, 最小値, 最大値 ] (変数x x_1~x_n)
# PARAMETERS  パラメータ情報の辞書
#             キー：FullPN
#             値：初期値
PARAMETERS = { 
    'Process:/:E:KmS' : 5.0,
    'Process:/:E:KcF' : 5.0 }

# 最大世代数
MAX_GENERATION   = 10

# 終了条件（充分に小さい残差平方和）
ENOUGH_S = 0.005

# 残差のヤコビアンを求める際のパラメータの差分の割合
DELTA = 0.01


# --------------------------------------------------------
# (1) 関数
# --------------------------------------------------------

def getTargetDataPoints( time_course, t_start = None, t_end = None, interval = None ):
    # ECD時系列データ（numpy.ndarray）または、同じデータ構造のリストから
    # 最適化に用いるデータポイントを抽出して、同じ形式の numpy.ndarray を返す。
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
            return np.array( _mid )
        else:
            return np.array( [[]] )
    
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
        return np.array( reduced_time_cource )
    else:
        return np.array( [[]] )


def calc_next_beta( ess_file, target_data_set, beta_set, delta ):
    r   = []
    J_r = []

    beta = np.array( [ beta_set.values() ] ).T
    print "bata: {}".format( beta.shape )

    for a_target_FullPN, a_target_time_series in target_data_set.items():
        for a_target_datapoint in a_target_time_series:
            r.append( a_target_datapoint[1] - beta_set['Vmax'] * a_target_datapoint[2] / ( beta_set['Km'] + a_target_datapoint[2] ) )
            _J_r = []
            for a_beta_FullPN, a_beta_value in beta_set.items():
                if a_beta_FullPN == 'Vmax':
                    _J_r.append( - a_target_datapoint[2] / ( beta_set['Km'] + a_target_datapoint[2] ) )
                elif a_beta_FullPN == 'Km':
                    _J_r.append( beta_set['Vmax'] * a_target_datapoint[2] / pow( beta_set['Km'] + a_target_datapoint[2], 2 ) )
            J_r.append( _J_r )

    S = 0.0
    for i in r:
        S += i * i

    r = np.array( [ r ] ).T
    print "r:  {}".format( r.shape )
    J_r = np.array( J_r )
    print "J_r:  {}".format( J_r.shape )

    beta_next = np.dot( np.linalg.inv( np.dot( J_r.T, J_r ) ), J_r.T )
    print "beta_next (1):  {}".format( beta_next.shape )
    beta_next = np.dot( beta_next, r )
    print "beta_next (2):  {}".format( beta_next.shape )
    beta_next = beta - beta_next
    print "beta_next (3):  {}".format( beta_next.shape )

#    beta_next = beta - np.dot( np.dot( np.linalg.inv( np.dot( J_r.T, J_r ) ), J_r.T ), beta )

#    print "beta_next:\n{}".format( beta_next.T[0] )

    for a_beta_FullPN, a_beta_next_value in zip( beta_set.keys(), beta_next.T[0].tolist() ):
        beta_set[ a_beta_FullPN ] = a_beta_next_value

    print "beta_next:\n{}".format( beta_set )

    return S, beta_set


# --------------------------------------------------------
# (2) データの準備
# --------------------------------------------------------

# 現時点のパラメータを格納する変数 beta を初期化
beta = copy.deepcopy( PARAMETERS )

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
target_data_set = {}

for FullPN, ECDFileName in CURVE_DATA_DICT.items():
    aTimeCouse = ECDDataFile()
    aTimeCouse.load( os.sep.join(( CURVE_DATA_DIR.rstrip( os.sep ), ECDFileName )) )
    target_data_set[ FullPN ] = getTargetDataPoints( aTimeCouse.getData(), T_START, T_END, T_INTERVAL )

# DEBUG: BEGIN
    beta = dict( Vmax = 0.9, Km = 0.2 )

    target_data_set = dict(
        v = np.array([
            [1, 0.0500, 0.038],
            [2, 0.1270, 0.194],
            [3, 0.0940, 0.425],
            [4, 0.2122, 0.626], 
            [5, 0.2729, 1.253],
            [6, 0.2665, 2.500],
            [7, 0.3317, 3.740]
        ])
    )

# DEBUG: END

for FullPN, tc in target_data_set.items():
    print "\n" + FullPN
    for dp in tc:
        print "{} : {}".format( dp[0], dp[1] )


# --------------------------------------------------------
# (3) 反復計算
# --------------------------------------------------------

for i in range( MAX_GENERATION ):
    
    # 現ラウンドの残差平方和 S と、次ラウンドのパラメータセットβ(S+1)（beta_next）を算出
    S, beta_next = calc_next_beta( ESS_FILE, target_data_set, beta, DELTA )
    
    if S <= ENOUGH_S:
        break
    else:
        beta = beta_next


# --------------------------------------------------------
# (4) 結果出力
# --------------------------------------------------------

for FullPN, p in beta_next.items():
    print "{} : {}".format( FullPN, p )
