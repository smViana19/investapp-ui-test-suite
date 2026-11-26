
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class PortfolioPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        # Campos do formulário
        self.select_ativo = page.locator(
            "[data-testid='select-asset-name']"
        )

        self.input_quantidade = page.locator(
            "[data-testid='input-asset-amount']"
        )

        self.input_preco_compra = page.locator(
            "[data-testid='input-asset-price']"
        )

        self.input_dias_investidos = page.locator(
            "[data-testid='input-asset-days-invested']"
        )

        self.input_dias_planejados = page.locator(
            "[data-testid='input-asset-planned-days']"
        )

        self.botao_adicionar = page.locator(
            "[data-testid='btn-add-asset']"
        )

        # Tabela e mensagens
        self.linhas_tabela_carteira = page.locator(
            "[data-testid='table-portfolio'] tbody tr"
        )

        self.alerta_erro = page.locator(
            "[data-testid='portfolio-error']"
        )

    def cadastrar_aporte(
        self,
        ativo: str,
        quantidade: str,
        preco: str,
        dias_inv: str,
        dias_plan: str
    ):

        self.select_ativo.wait_for(state="visible")

        try:
            self.select_ativo.select_option(value=ativo)
        except Exception:
            self.select_ativo.select_option(label=ativo)

        self.input_quantidade.fill(quantidade)
        self.input_preco_compra.fill(preco)
        self.input_dias_investidos.fill(dias_inv)
        self.input_dias_planejados.fill(dias_plan)

        self.botao_adicionar.click()

    def obter_linha_por_ativo_e_prazo(
        self,
        nome_ativo: str,
        dias_inv: str,
        dias_plan: str
    ) -> Locator:

        texto_prazo = f"{dias_inv} / {dias_plan} dias"

        return (
            self.linhas_tabela_carteira
            .filter(has_text=nome_ativo)
            .filter(has_text=texto_prazo)
            .first
        )
