FROM lineofflight/frankfurter

USER root
RUN mkdir -p /app/data && chown -R frankfurter:frankfurter /app/data
USER frankfurter
