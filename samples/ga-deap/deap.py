# -*- coding: utf-8 -*-
#
# This is a sample script file of EMS ( E-Cell Session Manager script )
# 

from ecell.ECDDataFile import *

import numpy as np
import os
import random
import copy

from deap import base
from deap import creator
from deap import tools

# --------------------------------------------------------
# (0) パラメータ設定
# --------------------------------------------------------
ESS_FILE       = 'session.py'

# トレーニングデータ（時系列）
TRAINING_DATA_DIR = 'Data'
TRAINING_DATA_DICT = {
    'Variable:/:S:Value' : 'S.ecd',
    'Variable:/:P:Value' : 'P.ecd' }

# Session毎に変化させる属性と値の値域
PARAMETER_RANGES = { 
    'Process:/:E:KmS' : [ 0.1, 20.0 ], 
    'Process:/:E:KcF' : [ 0.1, 20.0 ] }

MAX_GENERATION   = 4     # 最大世代数
POPULATION_SIZE  = 10     # 集団のサイズ（個体数）
FINISH_CONDITION = 0.005  # 終了条件

P_CX      = 0.2  # 交叉確率
P_MUT     = 0.5  # 変異確率
P_MUT_IND = 0.5  # 変異個体の各パラメータの変異確率

MUT_MU    = 0.0  # 変異量（正規分布）のパラメータ μ
MUT_SIGMA = 1.0  # 変異量（正規分布）のパラメータ σ

TOURNAMENT_SIZE = 4  # 選択のトーナメントサイズ

STDOUT_TIMEOUT = 0  # 標準入出力ファイルの書き込み時間のタイムアウト（整数）  0 の場合打ち切らない。

# --------------------------------------------------------
# (1) メタファクトリcreatorを用いて必要なクラスを作成する
# --------------------------------------------------------

# クラス creator.theFitness を作成
#     基底クラス base.Fitness
#     追加属性 weights＝タプル (1.0,)
creator.create( "Fitness", base.Fitness, weights=( -1.0, ))

# クラス creator.Individual を作成
#     基底クラス リスト
#     追加属性 fitness＝creator.Fitnessオブジェクト
creator.create( "Individual", dict, fitness=creator.Fitness, jobID=None, data=None )


# --------------------------------------------------------
# (2) Toolboxインスタンスに必要な関数を作成・登録する
# --------------------------------------------------------

# ToolBoxオブジェクトに関数を登録する
toolbox = base.Toolbox()

# toolbox.createInitialValuesDict( paramDict )
#     PARAMETER_RANGESの内容に沿って、個体の初期値を生成し、
#     辞書インスタンスとして返す。
def createInitialValuesDict( paramDict ):
    r = {}
    for aFullPN, aRange in paramDict.items():
        r[ aFullPN ] = random.uniform( aRange[0], aRange[1] )
    return r

toolbox.register( "createInitialValuesDict", createInitialValuesDict, PARAMETER_RANGES )

# toolbox.initAnIndividual()
#   toolbox.createInitialValuesDict()で初期化した
#   creator.Individualインスタンスを返す
toolbox.register( "initAnIndividual",
                 tools.initIterate, creator.Individual, toolbox.createInitialValuesDict )

# 関数 createPopulation( n = N )
#   toolbox.initAnIndividual()で初期化した
#   N個のcreator.Individualインスタンスからなるリストを返す。
toolbox.register( "createPopulation",
                 tools.initRepeat, list, toolbox.initAnIndividual )

# トレーニングデータリストを読み出す
def getTrainingTimeCourseDataDict( training_data_dict, data_dir ):
    trainingTimeCourseDataDict = {}

    for FullPN, ECDFileName in training_data_dict.items():
        aTimeCouse = ECDDataFile()
        aTimeCouse.load( os.sep.join(( data_dir.rstrip( os.sep ), ECDFileName )) )
        trainingTimeCourseDataDict[ FullPN ] = dict( ECDFileName = ECDFileName, ECDData = aTimeCouse )

    return trainingTimeCourseDataDict

toolbox.register( "getTrainingTimeCourseDataDict", 
                   getTrainingTimeCourseDataDict, 
                   TRAINING_DATA_DICT, TRAINING_DATA_DIR )

# Sessionに渡すパラメータ辞書を作成
def prepareParameterDict( ind, training_data_dict, data_dir ):
    FullPNValueDict = {}
    for FullPN, value in ind.items():
        FullPNValueDict[ FullPN ] = value

#    return { 
#        'PARAMETERS' : FullPNValueDict,
#        'TRAINING_TIME_COURSE_DATA_DICT' : toolbox.getTrainingTimeCourseDataDict }

    return { 
        'PARAMETERS'         : FullPNValueDict,
        'TRAINING_DATA_DICT' : training_data_dict,
        'TRAINING_DATA_DIR'  : data_dir }

toolbox.register( "prepareParameterDict", 
                   prepareParameterDict, 
                   training_data_dict = TRAINING_DATA_DICT, 
                   data_dir = TRAINING_DATA_DIR )


# 評価関数（適応度関数）
def evaluate( ind ):
    # ind - creator.Individualインスタンス
    try:
        print 'job ID = {}'.format( ind.jobID )
        print getStdout( ind.jobID )
        return float( getStdout( ind.jobID ).split()[ -1 ].strip() ),  # 標準出力の最後の１行
    except ValueError:
        pass

    return float('inf'),

toolbox.register( "evaluate", evaluate )

# 交叉（１点交叉）
def cxOnePoint( ind1, ind2 ):
    # i1, 12 - creator.Individualインスタンス
    _ind1 = copy.deepcopy( ind1 )
    _ind2 = copy.deepcopy( ind2 )
    FullPNs = ind1.keys()
    random.shuffle( FullPNs )
    point = random.randrange( 1, len( FullPNs ))
    # print "[{}] / [{}]".format( ",".join( FullPNs[ : point ] ), ",".join( FullPNs[ point : ] ) )
    for f in FullPNs[ : point ]:
        ind1[ f ] = _ind2[ f ]
        ind2[ f ] = _ind1[ f ]

toolbox.register( "mate", cxOnePoint )

# 変異（ガウス分布）
def mutate( ind, mu, sigma ):
    # ind - creator.Individualインスタンス
    for FullPN, value in ind.items():
        if random.random() < P_MUT_IND:
            ind[ FullPN ] = value + np.random.normal( mu, sigma )

toolbox.register( "mutate", mutate, mu = MUT_MU, sigma = MUT_SIGMA )

# 選択
toolbox.register( "select", tools.selTournament, tournsize = TOURNAMENT_SIZE )  # 選択関数


# --------------------------------------------------------
# (3) 初期集団の作成
# --------------------------------------------------------

random.seed( 0 )
p = toolbox.createPopulation( n = POPULATION_SIZE )


# --------------------------------------------------------
# (4) 初期集団の数値計算
# --------------------------------------------------------

for i in p:
    i.jobID = registerEcellSession( ESS_FILE, 
                  toolbox.prepareParameterDict( i ), 
                  [ TRAINING_DATA_DIR, ],
                  stdout_timeout = STDOUT_TIMEOUT )

run()


# --------------------------------------------------------
# (5) 各個体の適応度を確定（fitness.valuesに書き込む）
# --------------------------------------------------------
fitnesses = list( map( toolbox.evaluate, p ))
for i, w in zip( p, fitnesses ):
    i.fitness.values = w

print( "-- Initial Population --" )
for i in p:
    p_str = []
    for FullPN, value in i.items():
        p_str.append( "{} = {}".format( FullPN.split(':')[ -1 ], value ) )
    p_str.append( "w = {}".format( i.fitness.values[ 0 ] ) )
    print ", ".join( p_str )


# --------------------------------------------------------
# (6) 世代発展
# --------------------------------------------------------

for g in range( MAX_GENERATION ):
    print( "-- Generation {} --".format( g + 1 ))

    # --------------------------------------------------------
    # (6-1) 次世代の集団 offspring を作成
    # --------------------------------------------------------
    offspring = toolbox.select( p, len( p ))
    offspring = list( map( toolbox.clone, offspring ))  # toolbox.clone は、個体インスタンスを複製した上で、そのfitness.valueをクリアする。

    # --------------------------------------------------------
    # (6-2) 交叉
    # --------------------------------------------------------
    # 選択した個体群に交差と突然変異を適応する
    # 偶数番目と奇数番目の個体を取り出して交差
    for i_od, i_ev in zip(offspring[::2], offspring[1::2]):
        if random.random() < P_CX:
            toolbox.mate( i_od, i_ev )
            del i_od.fitness.values
            del i_ev.fitness.values

    # --------------------------------------------------------
    # (6-3) 突然変異
    # --------------------------------------------------------
    for i in offspring:
        if random.random() < P_MUT:
            toolbox.mutate( i )
            del i.fitness.values

    # --------------------------------------------------------
    # (6-4) 親世代から変化のあった個体のみ数値計算
    # --------------------------------------------------------
    invalid_ind = [ i for i in offspring if not i.fitness.valid ]

    for i in invalid_ind:
        i.jobID = registerEcellSession( ESS_FILE, 
                      toolbox.prepareParameterDict( i ), 
                      [ TRAINING_DATA_DIR, ], 
                      stdout_timeout = STDOUT_TIMEOUT )

    run()

    # --------------------------------------------------------
    # (6-5) 各個体の適応度を確定（fitness.valuesに書き込む）
    # --------------------------------------------------------
    fitnesses = map( toolbox.evaluate, invalid_ind )
    for i, w in zip( invalid_ind, fitnesses ):
        i.fitness.values = w

    # --------------------------------------------------------
    # (6-6) 集団の内容を次世代集団に置き換える
    # --------------------------------------------------------
    p[:] = offspring

    for i in p:
        p_str = []
        for FullPN, value in i.items():
            p_str.append( "{} = {}".format( FullPN.split(':')[ -1 ], value ) )
        p_str.append( "w = {}".format( i.fitness.values[ 0 ] ) )
        print ", ".join( p_str )

    # --------------------------------------------------------
    # (6-7) 終了判定
    # --------------------------------------------------------
    elite = tools.selBest( p , 1 )[ 0 ]
    if elite.fitness.values[ 0 ] < FINISH_CONDITION:
        break


# --------------------------------------------------------
# (7) 結果出力
# --------------------------------------------------------
print( "-- Result (the best parameter set) --" )
i_best = tools.selBest( p , 1 )[ 0 ]
p_str = []
for FullPN, value in i_best.items():
    p_str.append( "{} = {}".format( FullPN.split(':')[ -1 ], value ) )
p_str.append( "w = {}".format( i_best.fitness.values[ 0 ] ) )
print ", ".join( p_str )



'''
=====================================================================
deap.creator.create(name, base[, attribute[, ...]])
  http://deap.readthedocs.io/en/1.0.x/api/creator.html#deap.creator.create
  name      – 作成するクラスの名前
  base      – 継承する基底クラス
  attribute – （オプション）このクラスに追加する属性（複数も可）

=====================================================================
クラス deap.base.Fitness([values])
  http://deap.readthedocs.io/en/1.0.x/api/base.html#fitness
  パラメータ
    values - （オプション）適応度（fitness）の初期値。タプル型。
  属性
    dominates(other, obj=slice(None, None, None))
    valid   - 適応度が求められるように値が設定されているならTrueを、
              そうでなければFalseを返す。
    values  - タプル型。適応度の値。
              individual.fitness.values = values の書式で代入できる。
              del individual.fitness.values の書式でクリアできる（invalidになる）。
              individual.fitness.values の書式で読み出せる。
    weights - タプル型。valuesの各要素が適応度に与える影響
    wvalues - weightsによって重みづけされたvalues。
              valuesとweightsの対応する要素の積からなるタプル。
              初期値は ()

=====================================================================
deap.base.Toolbox.register(alias, method[, argument[, ...]])
  http://deap.readthedocs.io/en/1.0.x/api/base.html#deap.base.Toolbox.register
  Toolboxインスタンスに、関数functionを名称aliasとして登録する。
  alias    – 登録する関数の名称。同名の関数がすでに存在する場合上書きする。
  function – 名称aliasによって呼びだされる関数
  argument – （オプション）ひとつまたは複数の引数（キーワード引数も可）。
             名称aliasが呼ばれると、自動的に関数functionに渡される。

=====================================================================
deap.tools.initRepeat( container, func, n )
  http://deap.readthedocs.io/en/1.0.x/api/tools.html#deap.tools.initRepeat
  container – 関数funcが返す値を格納するインスタンスの型（クラス）
  func      – n回呼びだされてcontainerに書き込む値を返す関数。
  n         – 関数funcを繰り返す回数
  戻り値     - 関数funcの戻り値を格納したcontainerインスタンス
=====================================================================
'''
