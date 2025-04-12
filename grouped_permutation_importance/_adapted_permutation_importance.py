# Code is based on scikit-learns permutation importance.
import numpy as np
import pandas as pd
from sklearn.inspection._permutation_importance import check_random_state, \
    _weights_scorer


def _calculate_permutation_scores(estimator, X, y, sample_weight, col_idx,
                                  random_state, n_repeats, scorer):
    """Calculate score when `col_idx` is permuted."""
    random_state = check_random_state(random_state)

    # Work on a copy of X to to ensure thread-safety in case of threading based
    # parallelism. Furthermore, making a copy is also useful when the joblib
    # backend is 'loky' (default) or the old 'multiprocessing': in those cases,
    # if X is large it will be automatically be backed by a readonly memory map
    # (memmap). X.copy() on the other hand is always guaranteed to return a
    # writable data-structure whose columns can be shuffled inplace.
    X_permuted = X.copy()
    if hasattr(X_permuted, "iloc"):
        col_idx = [x for (x, y) in enumerate(X_permuted.columns) if y in col_idx]
    scores = np.zeros(n_repeats)
    shuffling_idx = np.arange(X.shape[0])
    for n_round in range(n_repeats):
        random_state.shuffle(shuffling_idx)
        if hasattr(X_permuted, "iloc"):
            X_permuted = np.array(X_permuted)
            X_permuted[:, col_idx] = X_permuted[[[x] for x in shuffling_idx], col_idx]
            X_permuted = pd.DataFrame(X_permuted, columns=X.columns)
        else:
            X_permuted[:, col_idx] = X_permuted[[[x] for x in shuffling_idx], col_idx]
        feature_score = _weights_scorer(
            scorer, estimator, X_permuted, y, sample_weight
        )
        scores[n_round] = feature_score

    return scores
