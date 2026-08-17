class ErrorAPI(Exception):
    """Error con forma conocida, mapeado por main.py a la envoltura de error del contrato
    (docs/architecture/contrato-api.md §1). Cualquier endpoint puede levantarlo directamente.
    """

    def __init__(self, codigo: str, mensaje: str, status_code: int) -> None:
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.status_code = status_code
