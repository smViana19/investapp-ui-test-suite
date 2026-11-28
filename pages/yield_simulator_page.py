from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class YieldSimulatorPage(BasePage):
    """Representa a aba Simulador de Rentabilidade Mês a Mês (YieldSimulator.jsx — US03)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Controles de projeção
        self.titulo_aba = page.get_by_role("heading", name="Projeção de Rendimento")
        self.input_meses = page.get_by_role("spinbutton")
        self.botao_simular = page.get_by_role("button", name="Calcular Evolução")

        # Resultados: tabela com uma linha por mês e uma coluna por ativo
        self.titulo_resultado = page.get_by_role("heading", name="Evolução Mês a Mês")
        self.tabela_rendimento = page.locator("main table").first
        self.linhas_meses = page.locator("main table tbody tr")
        self.coluna_total = page.get_by_role("columnheader", name="Total Carteira")

    def definir_meses(self, meses: int):
        """Ajusta o campo de projeção (1 a 60 meses)."""
        self.input_meses.wait_for(state="visible")
        self.input_meses.fill(str(meses))

    def simular(self):
        self.botao_simular.click()

    def simular_projecao(self, meses: int):
        """Fluxo completo: define o horizonte e dispara a simulação."""
        self.definir_meses(meses)
        self.simular()

    def obter_linha_do_mes(self, numero_mes: int) -> Locator:
        """Linha da tabela correspondente a 'Mês N'."""
        return self.linhas_meses.filter(has_text=f"Mês {numero_mes}").first

    def obter_coluna_ativo(self, nome_ativo: str) -> Locator:
        """Primeiro cabeçalho de coluna do tipo de ativo informado."""
        return self.tabela_rendimento.get_by_role("columnheader", name=nome_ativo).first