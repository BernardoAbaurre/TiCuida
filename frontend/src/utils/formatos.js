// Rótulos, cores (classes Bulma) e formatações usados em várias telas.

export const PRIORIDADES = {
  emergencia: { rotulo: 'Emergência', cor: 'is-danger' },
  urgente: { rotulo: 'Urgente', cor: 'is-warning' },
  pouco_urgente: { rotulo: 'Pouco urgente', cor: 'is-info' },
  nao_urgente: { rotulo: 'Não urgente', cor: 'is-success' },
}

export const LOTACAO = {
  baixa: { rotulo: 'Lotação baixa', curto: 'Baixa', cor: 'is-success' },
  media: { rotulo: 'Lotação média', curto: 'Média', cor: 'is-warning' },
  alta: { rotulo: 'Lotação alta', curto: 'Alta', cor: 'is-danger' },
}

export const STATUS = {
  a_caminho: { rotulo: 'A caminho', cor: 'is-info' },
  chegou: { rotulo: 'Chegou', cor: 'is-primary' },
  atendido: { rotulo: 'Atendido', cor: 'is-success' },
  nao_compareceu: { rotulo: 'Não compareceu', cor: 'is-dark' },
}

export const ACOES_STATUS = {
  chegou: { rotulo: 'Marcar chegada', cor: 'is-primary' },
  atendido: { rotulo: 'Marcar atendido', cor: 'is-success' },
  nao_compareceu: { rotulo: 'Não compareceu', cor: 'is-light' },
}

export const INICIOS_SINTOMAS = [
  { valor: 'menos_24h', rotulo: 'Menos de 24 horas' },
  { valor: '1_a_3_dias', rotulo: 'De 1 a 3 dias' },
  { valor: 'mais_3_dias', rotulo: 'Mais de 3 dias' },
]

export const TIPOS_UNIDADE = {
  pronto_atendimento: 'Pronto atendimento',
  clinica: 'Clínica',
  hospital: 'Hospital',
}

export function rotuloInicio(valor) {
  return INICIOS_SINTOMAS.find((i) => i.valor === valor)?.rotulo ?? valor
}

export function somenteDigitos(valor) {
  return String(valor ?? '').replace(/\D/g, '')
}

export function formatarTelefone(valor) {
  const d = somenteDigitos(valor)
  if (d.length === 11) return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`
  if (d.length === 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`
  return valor ?? ''
}

export function mascararCpf(valor) {
  const d = somenteDigitos(valor).slice(0, 11)
  return d
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/(\d{3})\.(\d{3})\.(\d{3})(\d)/, '$1.$2.$3-$4')
}

export function formatarDataHora(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

export function formatarData(isoData) {
  if (!isoData) return ''
  const [ano, mes, dia] = isoData.split('-')
  return `${dia}/${mes}/${ano}`
}

export function minutosDesde(iso) {
  return Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 60000))
}

export function tempoRelativo(iso) {
  const minutos = minutosDesde(iso)
  if (minutos < 1) return 'agora mesmo'
  if (minutos < 60) return `há ${minutos} min`
  const horas = Math.floor(minutos / 60)
  if (horas < 24) return `há ${horas} h`
  return `há ${Math.floor(horas / 24)} dia(s)`
}

export function linkRota(lat, lng) {
  return `https://www.openstreetmap.org/directions?to=${lat}%2C${lng}`
}
