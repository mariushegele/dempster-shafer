"""Emotion module

Determines plausibility and belief for all emotions in each 10 second
interval within the given CSV.

Expects a strings indicating the path to the CSV with the acoustic data.
Expects the CSV to be of format "geschwindigkeit;tonlage;schallstaerke".

Writes the output into a new CSV matching the file name in the 'results' folder.

Example Invocation:
        python emotion.py data/E_B02_Sequenz_1.csv
"""

import sys
import os
import pandas as pd

from dempster_shafer import BasicMeasure, accumulate


def discretize_cont_df(cont_df):
    """Discretizes the values into bins of low, normal and high

        Parameters:
            cont_df (pandas.DataFrame): set of continous values for
                'geschwindigkeit', 'tonlage' and 'schallstaerke'
        Returns:
            disc_df (pandas.DataFrame): set of discrete values
                each one of 'low', 'normal' or 'high'
    """
    lower_quartiles = {'geschwindigkeit': 82.5,
                       'tonlage': 140.0,
                       'schallstaerke': 28.0}
    upper_quartiles = {'geschwindigkeit': 110.5,
                       'tonlage': 265.0,
                       'schallstaerke': 49.0}

    disc_df = cont_df.copy()
    for col in cont_df:
        lower = lower_quartiles[col]
        upper = upper_quartiles[col]

        def _stringify(val, lower=lower, upper=upper):
            if val <= lower:
                return "low"
            if val >= upper:
                return "high"
            return "normal"

        disc_df[col] = cont_df[col].map(_stringify)
    return disc_df

def distribution_of_bins(discrete_window):
    """Determines the window's ratios for 'low', 'normal' and 'high'

        Parameters:
            discrete_window (pandas.DataFrame): a time frame containing
                multiple rows of binned values
        Returns:
            dist (dict): maps the each col to a 3-tuple indicating
                the ratios for 'low', 'normal' and 'high',
                e.g. 'tonlage': (0.3, 0.5, 0.2)
    """
    dist = {}

    for col in discrete_window:
        window_counts = dict(discrete_window[col].value_counts())
        dist[col] = tuple(window_counts.get(level, 0) / len(discrete_window)
                          for level in ('low', 'normal', 'high'))

    return dist

def normalized_intensity_std(window):
    """Normalizes the intensity's standard deviation to [0, 1]

        Parameters:
            window (pandas.DataFrame): a time frame containing
                multiple rows of continuous values
        Returns:
            win_std (float): a continous number in between 0 and 1
                indicating to which degree the intensity was high
                in this window
    """
    def _min_max_normalize(val, _min, _max):
        numerator = val - _min
        denominator = _max - _min
        return numerator / denominator

    win_std = window['schallstaerke'].std()

    global_max = 19.3
    global_min = 0.95

    return _min_max_normalize(win_std, global_min, global_max)


def main(csv_file): # pylint: disable=too-many-locals
    """Main procedure: discretize values, and for each window
    determine the distribution of bins
    as well the degree of standard deviation in the voice intensity.

    Then, construct basic measures out of the determined values,
    and accumulate them into single basic measure
    to determine the belief and plausibility for each emotion in the window.

    Finally, write the output into a 'csv' file in the 'results' folder.

    Parameters:
        csv_file (str): path to the CSV file containing continous values
            for each of the voice parameters
            'geschwindigkeit', 'tonlage' and 'schallstaerke'

    Returns:
        None
    """
    cont_df = pd.read_csv(csv_file, delimiter=';')

    A, U, W, F, E, T = ('Angst', 'Überraschung', 'Wut',
                        'Freude', 'Ekel', 'Traurigkeit')
    emotion_domain = {A, U, W, F, E, T}

    index = pd.MultiIndex.from_arrays([[]] * 4,
                                      names=(u'filename',
                                             u'window',
                                             u'metric',
                                             u'emotion'))
    results = pd.DataFrame(index=index, columns=['value'])

    disc_df = discretize_cont_df(cont_df)

    for i in range(len(cont_df) - 10 + 1):
        cont_window = cont_df[i:i+10]
        disc_window = disc_df[i:i+10]

        mSpeed = BasicMeasure(emotion_domain)
        mPitch = BasicMeasure(emotion_domain)
        mIntensity = BasicMeasure(emotion_domain)
        mIntensityStd = BasicMeasure(emotion_domain)

        # determine the ratio of how low, normal and high each feature is
        dist = distribution_of_bins(disc_window)

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
        intensity_std = normalized_intensity_std(cont_window)
        mIntensityStd.add_entry(T, intensity_std)

        # accumulate
        mAcc = accumulate(mSpeed, mPitch)
        mAcc = accumulate(mAcc, mIntensity)
        mAcc = accumulate(mAcc, mIntensityStd)

        for e in emotion_domain:
            results.loc[(csv_file, i, 'plausibility', e)] = mAcc.get_plausibility(e)
            results.loc[(csv_file, i, 'belief', e)] = mAcc.get_belief(e)
            results.loc[(csv_file, i, 'doubt', e)] = mAcc.get_doubt(e)

    print(results)
    results.to_csv(os.path.join('results', os.path.basename(csv_file)))

if __name__ == "__main__":
    CSV_FILE = None
    try:
        CSV_FILE = sys.argv[1]
    except:
        raise Exception("Provide CSV file of audio sequence as first argument")
    main(CSV_FILE)
