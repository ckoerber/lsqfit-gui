"""Plotting utility functions for distributions."""
from typing import Dict

import numpy as np
from scipy.stats import norm

import plotly.graph_objects as go


def get_p2p_fig(fit) -> Dict[str, go.Figure]:
    """Plot change of prior to posterior distribution."""
    figs = {}
    for n, (key, prior) in enumerate(fit.prior.items()):
        posterior = fit.p[key]
        fig = go.Figure(layout_title=key,)

        for which, val in [("prior", prior), ("posterior", posterior)]:
            x = np.linspace(val.mean - 3 * val.sdev, val.mean + 3 * val.sdev, 200)
            y = norm(val.mean, val.sdev).pdf(x)
            fig.add_trace(
                go.Scatter(x=x, y=y, fill="tozeroy", name=which, showlegend=n == 0,),
            )
        figs[key] = fig
    return figs
