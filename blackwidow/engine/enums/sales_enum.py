from enum import Enum

__author__ = 'Mahmud'


class ProductRejectReason(Enum):
    NotRejected = 0
    QualityDefect = 1
    TransportDamage = 2
    ExpiredProduct = 3

    @classmethod
    def get_name(cls,value):
        if value==cls.QualityDefect.value:
            return "Quality Defect"
        elif value==cls.TransportDamage.value:
            return "Transport Damage SC"
        elif value==cls.ExpiredProduct.value:
            return "Expired Product"
        else:
            return ""

    @classmethod
    def get_enum_list(cls):
        return [
            (str(cls.QualityDefect.value), cls.get_name(cls.QualityDefect.value)),
            (str(cls.TransportDamage.value), cls.get_name(cls.TransportDamage.value)),
            (str(cls.ExpiredProduct.value), cls.get_name(cls.ExpiredProduct.value)),
        ]


class ProductReturnReason(Enum):
    NotReturned = 0
    QualityDefect = 1
    TransportDamage = 2
    ExpiredProduct = 3

    @classmethod
    def get_name(cls,value):
        if value==cls.QualityDefect.value:
            return "Quality Defect"
        elif value==cls.TransportDamage.value:
            return "Transport Damage Sales"
        elif value==cls.ExpiredProduct.value:
            return "Market Return (Expired)"
        else:
            return ""

    @classmethod
    def get_enum_list(cls):
        return [
            (str(cls.QualityDefect.value), cls.get_name(cls.QualityDefect.value)),
            (str(cls.TransportDamage.value), cls.get_name(cls.TransportDamage.value)),
            (str(cls.ExpiredProduct.value), cls.get_name(cls.ExpiredProduct.value)),
        ]
