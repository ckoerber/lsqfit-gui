"""Example application of lsqfit-gui from the lsqfit documentation.

See also https://lsqfit.readthedocs.io/en/latest/lsqfit.html#lsqfit-multifitter-classes
"""

import lsqfitgui
import lsqfit
import numpy as np
import gvar as gv


class Linear(lsqfit.MultiFitterModel):
    def __init__(self, datatag, x, intercept, slope):
        super(Linear, self).__init__(datatag)
        self.x = np.array(x)
        self.intercept = intercept
        self.slope = slope

    def fitfcn(self, p):
        """Return linear fit function."""
        return p[self.intercept] + p[self.slope] * self.x

    def buildprior(self, prior, mopt=None):
        """Extract the model's parameters from prior."""
        newprior = {}
        newprior[self.intercept] = prior[self.intercept]
        newprior[self.slope] = prior[self.slope]
        return newprior

    def builddata(self, data):
        """Extract the model's fit data from data."""
        return data[self.datatag]


def main():
    lsqfitgui.run_server(fit_setup_function=make_fitter)


def make_fitter(**meta):
    """Generate a fit for specified meta information."""
    models = make_models()
    data = make_data()
    prior = make_prior()
    fitter = lsqfit.MultiFitter(models=models)
    fit = fitter.lsqfit(data=data, prior=prior)
    return fit


def make_models():
    return [
        Linear("d1", x=[1, 2, 3, 4], intercept="a", slope="s1"),
        Linear("d2", x=[1, 2, 3, 4], intercept="a", slope="s2"),
        Linear("d3", x=[1, 2, 3, 4], intercept="a", slope="s3"),
        Linear("d4", x=[1, 2, 3, 4], intercept="a", slope="s4"),
    ]


def make_prior():
    return gv.gvar(dict(a="0(1)", s1="0(1)", s2="0(1)", s3="0(1)", s4="0(1)"))


def make_data():
    return gv.gvar(
        dict(
            d1=["1.154(10)", "2.107(16)", "3.042(22)", "3.978(29)"],
            d2=["0.692(10)", "1.196(16)", "1.657(22)", "2.189(29)"],
            d3=["0.107(10)", "0.030(16)", "-0.027(22)", "-0.149(29)"],
            d4=["0.002(10)", "-0.197(16)", "-0.382(22)", "-0.627(29)"],
        )
    )


if __name__ == "__main__":
    main()
