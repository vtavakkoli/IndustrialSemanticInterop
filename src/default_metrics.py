"""
Contains the default performance metrics and summary used to generate
comparison figures.  These values are derived from the evaluation
results presented in the associated paper and provide a baseline for
comparison across different integration approaches (ontology-based,
direct protocol, service-oriented and OPC UA based).

The ``METRICS`` dictionary mirrors the structure expected by the
``generate_final_results`` module, and ``SUMMARY`` is a list of
dictionaries corresponding to rows in the performance summary.
"""

METRICS = {
    'latency': {
        'ontology_based': {
            'small_scale': {'avg': 4.768990186282669, 'min': 3.423364862037282, 'max': 6.209591296013463},
            'medium_scale': {'avg': 5.945284087525945, 'min': 4.301653422357917, 'max': 7.752344079222673},
            'large_scale': {'avg': 7.193004516735894, 'min': 5.425056190066238, 'max': 9.62073603234654},
        },
        'direct_protocol': {
            'small_scale': {'avg': 0.9732794028962418, 'min': 0.7111896950036275, 'max': 1.2410906064078948},
            'medium_scale': {'avg': 7.500315842691713, 'min': 5.031979306311001, 'max': 9.968652379072424},
            'large_scale': {'avg': 12.549816822080174, 'min': 9.058942727954587, 'max': 16.83613621846437},
        },
        'service_oriented': {
            'small_scale': {'avg': 2.863235741331556, 'min': 2.147153041168103, 'max': 3.721224478749846},
            'medium_scale': {'avg': 3.722836293910979, 'min': 2.568970193878313, 'max': 4.883054302998056},
            'large_scale': {'avg': 4.610853355095642, 'min': 3.114510387842043, 'max': 5.920413734086661},
        },
        'opcua_based': {
            'small_scale': {'avg': 1.9252529336095425, 'min': 1.392237385864766, 'max': 2.662695138616974},
            'medium_scale': {'avg': 2.465348364978595, 'min': 1.6894668587988888, 'max': 3.197810537529596},
            'large_scale': {'avg': 2.9686714171162776, 'min': 2.0207922462921077, 'max': 3.867402735738673},
        },
    },
    'throughput': {
        'ontology_based': {'small_scale': 504.39332437763306, 'medium_scale': 424.53521579814833, 'large_scale': 346.9714752023388},
        'direct_protocol': {'small_scale': 5052.953359476298, 'medium_scale': 4177.752710350646, 'large_scale': 3193.292082074766},
        'service_oriented': {'small_scale': 2063.4332522089494, 'medium_scale': 1601.8495329289337, 'large_scale': 1322.8026472595975},
        'opcua_based': {'small_scale': 3084.5874265398475, 'medium_scale': 2468.7915831422692, 'large_scale': 2015.6143465445061},
    },
    'cpu_usage': {
        'ontology_based': {'small_scale': 24.204029781841093, 'medium_scale': 52.668984731197675, 'large_scale': 100.0},
        'direct_protocol': {'small_scale': 10.581488606356228, 'medium_scale': 18.96870943348646, 'large_scale': 36.17368119113842},
        'service_oriented': {'small_scale': 20.973948367726795, 'medium_scale': 39.24870046296752, 'large_scale': 78.80544914477835},
        'opcua_based': {'small_scale': 15.266277071968103, 'medium_scale': 32.50658970916868, 'large_scale': 61.53541571428166},
    },
    'scalability': {
        'ontology_based': {
            '10': {'latency': 25.036721626147312, 'throughput': 498.7174091314116},
            '50': {'latency': 26.615999212421073, 'throughput': 441.9817984040464},
            '100': {'latency': 28.867862726425304, 'throughput': 467.18217431183314},
            '500': {'latency': 26.9968625086865, 'throughput': 422.0861401610626},
            '1000': {'latency': 28.8926667321097, 'throughput': 422.05308334185986},
            '5000': {'latency': 28.53274510092527, 'throughput': 406.588146964511},
        },
        'direct_protocol': {
            '10': {'latency': 4.920057496669282, 'throughput': 4977.818520387679},
            '50': {'latency': 5.31597681001519, 'throughput': 4707.845581134361},
            '100': {'latency': 5.019798423067753, 'throughput': 4929.403138902161},
            '500': {'latency': 5.368977042823138, 'throughput': 4956.83238357344},
            '1000': {'latency': 5.2041494868534866, 'throughput': 4616.752517275218},
            '5000': {'latency': 5.097642309625822, 'throughput': 4814.555081621611},
        },
        'service_oriented': {
            '10': {'latency': 15.665353167912437, 'throughput': 2047.6220687057491},
            '50': {'latency': 15.320665442691453, 'throughput': 1949.3835029237432},
            '100': {'latency': 16.137741088413865, 'throughput': 1897.0357444798956},
            '500': {'latency': 15.186983322460984, 'throughput': 1940.0640881053826},
            '1000': {'latency': 16.047915906530182, 'throughput': 1811.25346232024},
            '5000': {'latency': 15.326660676910464, 'throughput': 1842.5783038667682},
        },
        'opcua_based': {
            '10': {'latency': 9.943517579382576, 'throughput': 2890.411777954361},
            '50': {'latency': 9.896251874223834, 'throughput': 2826.960962188118},
            '100': {'latency': 10.60883641274512, 'throughput': 3036.3013515548682},
            '500': {'latency': 10.830387907409282, 'throughput': 2794.7238463538747},
            '1000': {'latency': 10.510449569041787, 'throughput': 2989.680598208696},
            '5000': {'latency': 10.840160617647635, 'throughput': 2752.284082292311},
        },
    },
    'security_overhead': {
        'ontology_based': {
            'none': {'latency_overhead': 0.0, 'throughput_reduction': 0.0},
            'authentication': {'latency_overhead': 16.07925118541661, 'throughput_reduction': 17.21330101094062},
            'encryption': {'latency_overhead': 31.14372197951931, 'throughput_reduction': 33.336206673017486},
            'full': {'latency_overhead': 47.23358320409419, 'throughput_reduction': 50.03368847950006},
        },
        'direct_protocol': {
            'none': {'latency_overhead': 0.0, 'throughput_reduction': 0.0},
            'authentication': {'latency_overhead': 4.9458634648073865, 'throughput_reduction': 5.92084112679346},
            'encryption': {'latency_overhead': 9.199842363180773, 'throughput_reduction': 12.590843799954325},
            'full': {'latency_overhead': 16.415527570388505, 'throughput_reduction': 17.651858456562458},
        },
        'service_oriented': {
            'none': {'latency_overhead': 0.0, 'throughput_reduction': 0.0},
            'authentication': {'latency_overhead': 10.768250138846282, 'throughput_reduction': 11.17619979348029},
            'encryption': {'latency_overhead': 21.529220294494706, 'throughput_reduction': 23.250693657265412},
            'full': {'latency_overhead': 28.84525893495632, 'throughput_reduction': 33.08651449796288},
        },
        'opcua_based': {
            'none': {'latency_overhead': 0.0, 'throughput_reduction': 0.0},
            'authentication': {'latency_overhead': 7.982445346810287, 'throughput_reduction': 9.302745283264299},
            'encryption': {'latency_overhead': 16.932813662457423, 'throughput_reduction': 18.528264283146335},
            'full': {'latency_overhead': 23.804244887449276, 'throughput_reduction': 27.99722724894299},
        },
    },
    'integration_time': {
        'ontology_based': {'configuration_time': 18.38666943974452, 'development_time': 84.47415943310268, 'total_time': 102.86082887284721},
        'direct_protocol': {'configuration_time': 10.515462278754272, 'development_time': 41.63783874257882, 'total_time': 52.15330102133309},
        'service_oriented': {'configuration_time': 15.249572419664394, 'development_time': 61.505850974855946, 'total_time': 76.75542339452034},
        'opcua_based': {'configuration_time': 12.91754461185829, 'development_time': 51.06035900819019, 'total_time': 63.97790362004848},
    },
    # Message size used in the summary (medium scale values)
    'message_size': {
        'ontology_based': {'small_scale': 5.945284087525945, 'medium_scale': 5.945284087525945, 'large_scale': 5.945284087525945},
        'direct_protocol': {'small_scale': 1.18567613374989, 'medium_scale': 1.18567613374989, 'large_scale': 1.18567613374989},
        'service_oriented': {'small_scale': 3.722836293910979, 'medium_scale': 3.722836293910979, 'large_scale': 3.722836293910979},
        'opcua_based': {'small_scale': 2.465348364978595, 'medium_scale': 2.465348364978595, 'large_scale': 2.465348364978595},
    },
}

# Performance summary table data.  Each dictionary corresponds to a row in
# ``performance_summary.csv``.  It is important to align column names
# exactly with those expected by the summary CSV.
SUMMARY = [
    {
        'Method': 'ontology_based',
        'Latency (ms)': 37.541205362818815,
        'Throughput (msg/s)': 424.53521579814833,
        'CPU Usage (%)': 52.668984731197675,
        'Memory Usage (MB)': 423.82956939088604,
        'Scalability (ms @ 1000)': 28.8926667321097,
        'Security Overhead (%)': 47.23358320409419,
        'Integration Time (h)': 102.86082887284721,
        'Message Size (KB)': 5.945284087525945,
    },
    {
        'Method': 'direct_protocol',
        'Latency (ms)': 7.500315842691713,
        'Throughput (msg/s)': 4177.752710350646,
        'CPU Usage (%)': 18.96870943348646,
        'Memory Usage (MB)': 105.22568256491705,
        'Scalability (ms @ 1000)': 5.2041494868534866,
        'Security Overhead (%)': 16.415527570388505,
        'Integration Time (h)': 52.15330102133309,
        'Message Size (KB)': 1.18567613374989,
    },
    {
        'Method': 'service_oriented',
        'Latency (ms)': 22.602158807538473,
        'Throughput (msg/s)': 1601.8495329289337,
        'CPU Usage (%)': 39.24870046296752,
        'Memory Usage (MB)': 300.4454475490362,
        'Scalability (ms @ 1000)': 16.047915906530182,
        'Security Overhead (%)': 28.84525893495632,
        'Integration Time (h)': 76.75542339452034,
        'Message Size (KB)': 3.722836293910979,
    },
    {
        'Method': 'opcua_based',
        'Latency (ms)': 14.902626865268248,
        'Throughput (msg/s)': 2468.7915831422692,
        'CPU Usage (%)': 32.50658970916868,
        'Memory Usage (MB)': 210.2544001710913,
        'Scalability (ms @ 1000)': 10.510449569041787,
        'Security Overhead (%)': 23.804244887449276,
        'Integration Time (h)': 63.97790362004848,
        'Message Size (KB)': 2.465348364978595,
    },
]