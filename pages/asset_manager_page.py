
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class AssetManagerPage(BasePage):
    """Representa a aba Gerenciar Taxas (US05)."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.tabela_taxas = page.locator(
            "[data-testid='table-asset-rates']"
        )

        self.linhas_tabela = self.tabela_taxas.locator(
            "tbody tr"
        )

        self.titulo = page.get_by_text(
            "Configuração das Taxas de Rentabilidade",
            exact=False
        )

    def obter_linha_ativo(self, nome_ativo: str) -> Locator:
        """Localiza a linha correspondente ao ativo."""
        return self.linhas_tabela.filter(
            has=self.page.get_by_text(
                nome_ativo, exact=True
            )
        )

    def obter_campo_taxa(self, nome_ativo: str) -> Locator:
        """Localiza o campo de edição da taxa anual."""
        return self.obter_linha_ativo(nome_ativo).locator(
            "input"
        )

    def obter_taxa_anual(self, nome_ativo: str) -> str:
        """Retorna o valor atual do campo de taxa."""
        return self.obter_campo_taxa(
            nome_ativo
        ).input_value()

    def obter_taxa_salva(self, nome_ativo: str) -> Locator:
        """Localiza a coluna da taxa anual salva."""
        return self.obter_linha_ativo(nome_ativo).locator(
            "td"
        ).nth(2)

    def alterar_taxa_anual(self, nome_ativo: str, taxa: str):
        """Preenche o campo com a nova taxa."""
        campo = self.obter_campo_taxa(nome_ativo)
        campo.fill(taxa)

    def salvar_taxa(self, nome_ativo: str):
        """Aciona o botão Salvar Alteração."""
        self.obter_linha_ativo(nome_ativo).get_by_role(
            "button",
            name="Salvar Alteração"
        ).click()

    def aguardar_tabela(self):
        """Aguarda a tabela e seus registros."""
        expect(self.tabela_taxas).to_be_visible(
            timeout=10000
        )

        expect(self.linhas_tabela.first).to_be_visible(
            timeout=10000
        )
