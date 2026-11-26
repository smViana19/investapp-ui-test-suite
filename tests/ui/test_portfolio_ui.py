
from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def test_cadastrar_novo_aporte_carteira(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage
):

    # Acessar a carteira
    navbar.navegar_para_carteira()

    # Dados do investimento
    ativo = "Poupança"
    quantidade = "2500.00"
    preco = "1.00"
    dias_inv = "0"
    dias_plan = "365"

    # Cadastrar o investimento
    portfolio_page.cadastrar_aporte(
        ativo=ativo,
        quantidade=quantidade,
        preco=preco,
        dias_inv=dias_inv,
        dias_plan=dias_plan
    )

    # Localizar o aporte cadastrado
    linha_aporte = (
        portfolio_page.obter_linha_por_ativo_e_prazo(
            ativo,
            dias_inv,
            dias_plan
        )
    )

    # Verificar se apareceu na tabela
    expect(linha_aporte).to_be_visible(timeout=10000)

    # Verificar o nome do ativo
    expect(linha_aporte).to_contain_text("Poupança")
