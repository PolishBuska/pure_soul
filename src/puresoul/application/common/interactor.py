from typing import TypeVar, Generic, List

InputDTO = TypeVar('InputDTO')
OutputDTO = TypeVar('OutputDTO')
ArrayDTO = TypeVar('ArrayDTO')

class Interactor(
        Generic[InputDTO, OutputDTO]
):
    async def __call__(self, input_dto: InputDTO) -> OutputDTO:
        raise NotImplementedError()
