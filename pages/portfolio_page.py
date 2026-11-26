import re

from playwright.sync_api import Page, Locator, Dialog
from pages.base_page import BasePage


class PortfolioPage(BasePage):
    """Representa a aba Carteira (Portfolio.jsx — US02).

    Concentra o formulário de novo aporte, o card de Patrimônio Total
    e a tabela de ativos com seus botões de exclusão.
    """

    SELETOR_BOTAO_EXCLUIR = "[data-testid^='btn-delete-asset-']"

    def __init__(self, page: Page):
        super().__init__(page)

        # Formulário de novo aporte
        self.select_ativo = page.locator("[data-testid='select-asset-name']")
        self.input_quantidade = page.locator("[data-testid='input-asset-amount']")
        self.input_preco_compra = page.locator("[data-testid='input-asset-price']")
        self.input_dias_investidos = page.locator("[data-testid='input-asset-days-invested']")
        self.input_dias_planejados = page.locator("[data-testid='input-asset-planned-days']")
        self.botao_adicionar = page.locator("[data-testid='btn-add-asset']")

        # Indicadores e tabela
        self.card_patrimonio_total = page.locator("[data-testid='summary-current-val']")
        self.linhas_tabela_carteira = page.locator("[data-testid='table-portfolio'] tbody tr")
        self.linhas_com_ativo = self.linhas_tabela_carteira.filter(
            has=page.locator(self.SELETOR_BOTAO_EXCLUIR)
        )
        self.botoes_excluir = page.locator(self.SELETOR_BOTAO_EXCLUIR)
        self.alerta_erro = page.locator("[data-testid='portfolio-error']")

        # Última mensagem de confirmação (window.confirm) exibida na exclusão
        self.ultima_mensagem_confirmacao: str | None = None

    # ------------------------------------------------------------------
    # Cadastro (US02 — Integrante 3)
    # ------------------------------------------------------------------
    def selecionar_ativo(self, nome_ativo: str):
        self.select_ativo.wait_for(state="visible")
        try:
            self.select_ativo.select_option(value=nome_ativo, timeout=2000)
        except Exception:
            self.select_ativo.select_option(label=nome_ativo)

    def cadastrar_aporte(self, ativo: str, quantidade, preco, dias_inv, dias_plan):
        """Preenche o formulário de novo aporte e confirma a inclusão."""
        self.selecionar_ativo(ativo)
        self.input_quantidade.fill(str(quantidade))
        self.input_preco_compra.fill(str(preco))
        self.input_dias_investidos.fill(str(dias_inv))
        self.input_dias_planejados.fill(str(dias_plan))
        self.botao_adicionar.click()

    def obter_linha_por_ativo_e_prazo(self, nome_ativo: str, dias_inv, dias_plan) -> Locator:
        """Linha da tabela que contém o ativo e o prazo 'dias investidos / dias planejados'."""
        padrao_prazo = re.compile(rf"\b{dias_inv}\s*/\s*{dias_plan}\b")
        return (
            self.linhas_com_ativo
            .filter(has_text=nome_ativo)
            .filter(has_text=padrao_prazo)
        )

    def obter_ultimo_ativo_cadastrado(self, nome_ativo: str) -> Locator:
        return self.linhas_com_ativo.filter(has_text=nome_ativo).last

    # ------------------------------------------------------------------
    # Exclusão e métricas consolidadas (US02 — Integrante 4)
    # ------------------------------------------------------------------
    def _registrar_tratamento_confirmacao(self, aceitar: bool):
        """Prepara a resposta ao alerta nativo de confirmação antes do clique."""
        self.ultima_mensagem_confirmacao = None

        def _tratar(dialog: Dialog):
            self.ultima_mensagem_confirmacao = dialog.message
            if aceitar:
                dialog.accept()
            else:
                dialog.dismiss()

        self.page.once("dialog", _tratar)

    def excluir_linha(self, linha: Locator, confirmar: bool = True):
        """Clica no botão de exclusão da linha e responde ao alerta de confirmação."""
        self._registrar_tratamento_confirmacao(confirmar)
        linha.locator(self.SELETOR_BOTAO_EXCLUIR).first.click()

    def excluir_primeiro_ativo(self, confirmar: bool = True):
        self.excluir_linha(self.linhas_com_ativo.first, confirmar)

    def excluir_ativo_por_prazo(self, nome_ativo: str, dias_inv, dias_plan, confirmar: bool = True):
        linha = self.obter_linha_por_ativo_e_prazo(nome_ativo, dias_inv, dias_plan).first
        self.excluir_linha(linha, confirmar)

    def total_de_ativos_listados(self) -> int:
        """Quantidade de linhas com ativo (ignora a linha de estado vazio)."""
        return self.linhas_com_ativo.count()

    def obter_texto_patrimonio_total(self) -> str:
        self.card_patrimonio_total.wait_for(state="visible")
        return self.card_patrimonio_total.inner_text().strip()

    def obter_valor_patrimonio_total(self) -> float:
        """Converte o texto do card (ex.: 'R$ 1.234,56') em float."""
        return self.converter_moeda(self.obter_texto_patrimonio_total())

    @staticmethod
    def converter_moeda(texto: str) -> float:
        numero = re.sub(r"[^\d,.\-]", "", texto)
        if not numero:
            return 0.0
        if "," in numero:
            # Formato brasileiro: ponto como milhar, vírgula como decimal
            numero = numero.replace(".", "").replace(",", ".")
        return float(numero)