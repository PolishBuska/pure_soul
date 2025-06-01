from typing import TypeVar, Generic

InputDTO = TypeVar('InputDTO')
OutputDTO = TypeVar('OutputDTO')

class Interactor(Generic[InputDTO, OutputDTO]):
    async def __call__(self, input_dto: InputDTO) -> OutputDTO:
        raise NotImplementedError()
