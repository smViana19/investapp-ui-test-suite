
import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.asset_manager_page import AssetManagerPage


@pytest.fixture
def asset_manager_page(page: Page) -> AssetManagerPage:
    return AssetManagerPage(page)


def test_visualizar_tabela_publica_taxas(
    page: Page,
    base_url: str,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage
):
    """US05: Verifica a visualização pública das taxas."""

    page.goto(base_url)

    expect(navbar.botao_entrar).to_be_visible()

    expect(
        navbar.link_gerenciar_taxas
    ).to_be_visible(timeout=5000)

    navbar.navegar_para_gerenciar_taxas()
    asset_manager_page.aguardar_tabela()

    expect(
        asset_manager_page.obter_linha_ativo("Poupança")
    ).to_be_visible()

    expect(
        asset_manager_page.obter_linha_ativo("CDB")
    ).to_be_visible()


def test_alterar_taxa_anual_ativo(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage
):
    """US05: Valida a alteração da taxa anual."""

    navbar.navegar_para_gerenciar_taxas()
    asset_manager_page.aguardar_tabela()

    ativo = "Poupança"

    taxa_original = asset_manager_page.obter_taxa_anual(
        ativo
    )

    nova_taxa = (
        "8.50" if float(taxa_original) != 8.50 else "9.00"
    )

    try:
        asset_manager_page.alterar_taxa_anual(
            ativo, nova_taxa
        )

        asset_manager_page.salvar_taxa(ativo)

        expect(
            asset_manager_page.obter_taxa_salva(ativo)
        ).to_contain_text(
            f"{float(nova_taxa):.2f}%",
            timeout=10000
        )

    finally:
        asset_manager_page.alterar_taxa_anual(
            ativo, taxa_original
        )

        asset_manager_page.salvar_taxa(ativo)

        expect(
            asset_manager_page.obter_taxa_salva(ativo)
        ).to_contain_text(
            f"{float(taxa_original):.2f}%",
            timeout=10000
        )


def test_persistencia_taxa_anual(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage
):
    """US05: Valida a persistência após recarregar."""

    navbar.navegar_para_gerenciar_taxas()
    asset_manager_page.aguardar_tabela()

    ativo = "Poupança"

    taxa_original = asset_manager_page.obter_taxa_anual(
        ativo
    )

    nova_taxa = (
        "9.50" if float(taxa_original) != 9.50 else "10.00"
    )

    try:
        asset_manager_page.alterar_taxa_anual(
            ativo, nova_taxa
        )

        asset_manager_page.salvar_taxa(ativo)

        expect(
            asset_manager_page.obter_taxa_salva(ativo)
        ).to_contain_text(
            f"{float(nova_taxa):.2f}%",
            timeout=10000
        )

        asset_manager_page.recarregar()

        navbar.navegar_para_gerenciar_taxas()
        asset_manager_page.aguardar_tabela()

        expect(
            asset_manager_page.obter_taxa_salva(ativo)
        ).to_contain_text(
            f"{float(nova_taxa):.2f}%",
            timeout=10000
        )

    finally:
        asset_manager_page.alterar_taxa_anual(
            ativo, taxa_original
        )

        asset_manager_page.salvar_taxa(ativo)

        expect(
            asset_manager_page.obter_taxa_salva(ativo)
        ).to_contain_text(
            f"{float(taxa_original):.2f}%",
            timeout=10000
        )
