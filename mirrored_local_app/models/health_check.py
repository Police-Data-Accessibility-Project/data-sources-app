from pydantic import BaseModel


class HealthCheckInfo(BaseModel):
    test: list[str]
    interval: int
    timeout: int
    retries: int
    start_period: int

    def build_healthcheck(self) -> dict:
        multiplicative_factor = 1000000000  # Assume 1 second
        return {
            "test": self.test,
            "interval": self.interval * multiplicative_factor,
            "timeout": self.timeout * multiplicative_factor,
            "retries": self.retries,
            "start_period": self.start_period * multiplicative_factor,
        }
