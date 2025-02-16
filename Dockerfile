ARG CAIPIRINHA_HOME_ARG=/usr/local/caipirinha

FROM python:3.8.20-slim-bullseye AS base
ARG CAIPIRINHA_HOME_ARG
ENV CAIPIRINHA_HOME=$CAIPIRINHA_HOME_ARG
WORKDIR $CAIPIRINHA_HOME
# Install system dependencies for building Python packages
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential libpq-dev \
#    && pip install -U pip && pip install -U uv \
#    && apt-get autoremove -y \
#    && apt-get clean

RUN pip install -U pip && pip install -U uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Copy and install dependencies using a cache-mounted directory
COPY pyproject.toml $CAIPIRINHA_HOME/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock && \
    uv sync --frozen --no-install-project --no-dev

FROM python:3.8.20-slim-bullseye AS final
ARG CAIPIRINHA_HOME_ARG
# Enable bytecode compilation and copy mode for UV tool before calling uv
ENV CAIPIRINHA_HOME=$CAIPIRINHA_HOME_ARG
ENV CAIPIRINHA_CONFIG=$CAIPIRINHA_HOME/conf/caipirinha-config.yaml
ENV PATH="$CAIPIRINHA_HOME/.venv/bin:$PATH"
WORKDIR $CAIPIRINHA_HOME

# Install dumb-init for better signal handling
RUN apt-get update && apt-get install -y --no-install-recommends dumb-init \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . $CAIPIRINHA_HOME
# Copy files from previous stages
COPY --from=base $CAIPIRINHA_HOME/.venv $CAIPIRINHA_HOME/.venv
COPY bin/entrypoint /usr/local/bin/

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint"]
CMD ["server"]
