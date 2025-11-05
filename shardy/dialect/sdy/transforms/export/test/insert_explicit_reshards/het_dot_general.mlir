sdy.mesh @mesh = <["model"=8, "batch"=4]>

func.func @dot_compatible_contracting_unsharded(
    %lhs: tensor<544x8192xbf16> {sdy.sharding = #sdy.sharding<@mesh, [{"batch"}, {}]>},
    %rhs: tensor<8192x1024xbf16> {sdy.sharding = #sdy.sharding<@mesh, [{"batch"}, {"model"}]>})
    -> (tensor<544x1024xbf16> {sdy.sharding = #sdy.sharding<@mesh, [{"batch"}, {"model"}]>}) {
  %res = stablehlo.dot_general %lhs, %rhs, contracting_dims = [1] x [0] {sdy.sharding = #sdy.sharding_per_value<[<@mesh, [{"batch"}, {"model"}]>]>} : (tensor<544x8192xbf16>, tensor<8192x1024xbf16>) -> tensor<544x1024xbf16>
  return %res : tensor<544x1024xbf16>
}
