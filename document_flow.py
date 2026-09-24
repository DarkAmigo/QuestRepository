from abc import ABC, abstractmethod


class Document(ABC):

    @abstractmethod
    def render(self) -> str:
        pass


class Report(Document):

    def render(self) -> str:
        return "Рендеринг звіту"


class Invoice(Document):

    def render(self) -> str:
        return "Рендеринг рахунку"


class Contract(Document):

    def render(self) -> str:
        return "Рендеринг контракту"


class DocumentFactory:

    @staticmethod
    def create(doc_type: str) -> Document:

        if doc_type == "report":
            return Report()

        elif doc_type == "invoice":
            return Invoice()

        elif doc_type == "contract":
            return Contract()

        else:
            raise ValueError(f"Невідомий тип документа: {doc_type}")
        

doc_type = input("Введіть тип документа: ")

document = DocumentFactory.create(doc_type)

print(document.render())