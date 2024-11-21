from dataclasses import dataclass
from typing import Generic, Literal, Type, TypeVar

ResultT = TypeVar("ResultT")
FailT = TypeVar("FailT")
T = TypeVar("T", bound="parent")


@dataclass(frozen=True, slots=True)
class Result(Generic[ResultT, FailT]):
    _value: ResultT | None
    _answers: FailT | None

    def __post_init__(self) -> None:
        assert self._validate()  # One can compile this away if performance is an issue (-OO flag)

    def _validate(self) -> Literal[True]:
        if self._value is not None and self._answers is not None:
            raise TypeError("Only value or answers allowed")
        if self._value is None and self._answers is None:
            raise TypeError("Either value or answers must be set")
        return True

    def __bool__(self) -> bool:
        return self.succeeded

    @property
    def succeeded(self) -> bool:
        return self._value is not None

    @property
    def failed(self) -> bool:
        return not self.succeeded

    @classmethod
    def from_success(cls: Type[T], result: ResultT) -> T:
        return cls(result, None)

    @classmethod
    def from_failure(cls: Type[T], answer: FailT) -> T:
        return cls(None, answer)

    @property
    def value(self) -> ResultT:
        if self.succeeded:
            return self._value  # noqa
        raise ValueError(f"tried to get a value from failed result\n{self}")

    @property
    def answer(self) -> FailT:
        if self.failed:
            return self._answers  # noqa
        raise ValueError(f"tried to get answers from successful result\n{self}")
