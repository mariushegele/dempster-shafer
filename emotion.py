from dempster import BasicMeasure, accumulate
import sys
import os
import pandas as pd

def discretize_window(window):
    lower_quartiles = {'geschwindigkeit': 82.5,
                       'tonlage': 140.0,
                       'schallstaerke': 28.0}
    upper_quartiles = {'geschwindigkeit': 110.5,
                       'tonlage': 265.0,
                       'schallstaerke': 49.0}

    def _stringify(x, lower, upper):
        if x <= lower: return "low"
        if x >= upper: return "high"
        return "normal"

    for col in window:
        window[col] = window[col].map(lambda entry: _stringify(entry,
                                                 lower_quartiles[col],
                                                 upper_quartiles[col]))
    return window

def discrete_distribution(discrete_window):
    dist = {}

    for col in discrete_window:
        window_counts = dict(discrete_window[col].value_counts())
        dist[col] = tuple(window_counts.get(level, 0) / len(discrete_window)
                          for level in ('low', 'normal', 'high'))

    return dist

def normalized_intensity_std(window):
    def _min_max_normalize(x, _min, _max):
        numerator = win_std - _min
        denominator = _max - _min
        return numerator / denominator

    win_std = window['schallstaerke'].std()

    global_max = 19.3
    global_min = 0.95

    return _min_max_normalize(win_std, global_min, global_max)


def main(csv_file):
    df = pd.read_csv(csv_file, delimiter=';')

    A, U, W, F, E, T = ('Angst', 'Überraschung', 'Wut',
                       'Freude', 'Ekel', 'Traurigkeit')
    emotion_domain = {A, U, W, F, E, T}

    index = pd.MultiIndex.from_arrays([[]] * 4, names=(u'filename', u'window', u'metric', u'emotion'))
    results = pd.DataFrame(index=index, columns=['value'])

    for i in range(len(df) - 10 + 1):
        window = df[i:i+10]

        mSpeed = BasicMeasure(emotion_domain)
        mPitch = BasicMeasure(emotion_domain)
        mIntensity = BasicMeasure(emotion_domain)
        mIntensityStd = BasicMeasure(emotion_domain)

        # determine the degree of how low, normal and high each feature is
        discrete_window = discretize_window(df.copy())
        dist = discrete_distribution(discrete_window)

        speed_low, _, speed_high = dist.get('geschwindigkeit')
        mSpeed.add_entry({A, U, W, F}, speed_high)
        mSpeed.add_entry({F, E}, speed_low)

        pitch_low, _, pitch_high = dist.get('tonlage')
        mPitch.add_entry({A, U, W, F}, pitch_high)
        mPitch.add_entry({E, T}, pitch_low)

        intensity_low, _, intensity_high = dist.get('schallstaerke')
        mIntensity.add_entry({U, W, F}, intensity_high)
        mIntensity.add_entry({T}, intensity_low)

        # also determine how strength of deviation in the intensity
        intensity_std = normalized_intensity_std(window)
        mIntensityStd.add_entry(T, intensity_std)

        # accumulate
        mAcc = accumulate(mSpeed, mPitch)
        mAcc = accumulate(mAcc, mIntensity)
        mAcc = accumulate(mAcc, mIntensityStd)

        plausibilities = {e: mAcc.get_plausibility(e) for e in emotion_domain}
        beliefs = {e: mAcc.get_belief(e) for e in emotion_domain}

        for e in emotion_domain:
            results.loc[(csv_file, i, 'plausibility', e)] = mAcc.get_plausibility(e)
            results.loc[(csv_file, i, 'belief', e)] = mAcc.get_belief(e)
            results.loc[(csv_file, i, 'doubt', e)] = mAcc.get_doubt(e)

    print(results)
    results.to_csv(os.path.join('results', os.path.basename(csv_file)))


if __name__ == "__main__":
    csv_file = None
    try:
        csv_file = sys.argv[1]
    except:
        raise Exception("Provide CSV file of audio sequence as first argument")
    main(csv_file)
