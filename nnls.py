import numpy as np
from scipy import optimize
from sklearn.linear_model import base
from sklearn.linear_model.base import _rescale_data
from sklearn.utils import check_X_y


class NNLS(base.LinearModel):
    def __init__(self, fit_intercept=True, normalize=False, copy_X=True):
        """
        Non negative least squares
        """
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X

    def fit(self, X, y, sample_weight=None):
        """
        Fit linear model.
        Parameters
        ----------
        X : numpy array [n_samples,n_features]
            Training data
        y : numpy array of shape [n_samples]
            Target values
        sample_weight : numpy array of shape [n_samples]
            Individual weights for each sample
        Returns
        -------
        self : returns an instance of self.
        """
        X, y = check_X_y(X, y,
                         y_numeric=True, multi_output=True)

        if (sample_weight is not None) and \
           np.atleast_1d(sample_weight).ndim > 1:
            raise ValueError("Sample weights must be 1D array or scalar")

        X, y, X_offset, y_offset, X_scale = self._preprocess_data(
            X, y, fit_intercept=self.fit_intercept, normalize=self.normalize,
            copy=self.copy_X, sample_weight=sample_weight)

        if sample_weight is not None:
            # Sample weight can be implemented via a simple rescaling.
            X, y = _rescale_data(X, y, sample_weight)

        self.coef_, _ = optimize.nnls(X, y)
        self._set_intercept(X_offset, y_offset, X_scale)

        return self