package com.mechanicaluniverse;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.*;
import java.util.*;
@Mod(MechanicalUniverse.ID)
public class MechanicalUniverse {
 public static final String ID="mechanicaluniverse";
 static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,ID);
 static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,ID);
 static final List<RegistryObject<Item>> TAB_ITEMS=new ArrayList<>();
 static final DeferredRegister<CreativeModeTab> CREATIVE_TABS=DeferredRegister.create(Registries.CREATIVE_MODE_TAB,ID);
 static final Map<String,List<RegistryObject<Item>>> GROUP_ITEMS=new LinkedHashMap<>();
 static final String[] TAB_NAMES={"main","rotation","engines","fluids","electronics","automation","transport","processing","structures"};
 private static String tabFor(String id) {
  if(id.contains("_transmission_")||id.contains("_shaft_"))return "rotation";
  if(id.contains("_engine_")||id.contains("_machine_"))return "engines";
  if(id.contains("_hydraulic_")||id.contains("_pneumatic_"))return "fluids";
  if(id.contains("_electric_")||id.contains("_control_"))return "electronics";
  if(id.contains("_logistics_")||id.contains("_robotics_"))return "automation";
  if(id.contains("_vehicle_")||id.contains("_construction_"))return "transport";
  if(id.contains("_chemistry_")||id.contains("_fluid_"))return "processing";
  if(id.contains("_structure_"))return "structures";
  return "main";
 }
 static void registerCreativeTab(String key) {
  CREATIVE_TABS.register(key,()->CreativeModeTab.builder()
   .title(Component.translatable("itemGroup.mechanicaluniverse."+key))
   .icon(()->new ItemStack(switch(key){
    case "rotation"->Items.IRON_INGOT;
    case "engines"->Items.PISTON;
    case "fluids"->Items.WATER_BUCKET;
    case "electronics"->Items.REDSTONE;
    case "automation"->Items.HOPPER;
    case "transport"->Items.MINECART;
    case "processing"->Items.BLAST_FURNACE;
    case "structures"->Items.IRON_BARS;
    default->Items.CRAFTING_TABLE;
   }))
   .displayItems((parameters,output)->{
    for(RegistryObject<Item> item:GROUP_ITEMS.getOrDefault(key,Collections.emptyList()))output.accept(item.get());
   }).build());
 }
 static void part(String key) {
  RegistryObject<Block> b=BLOCKS.register(key,()->new Block(BlockBehaviour.Properties.copy(Blocks.IRON_BLOCK)));
  RegistryObject<Item> item=ITEMS.register(key,()->new BlockItem(b.get(),new Item.Properties()));
  TAB_ITEMS.add(item);
  GROUP_ITEMS.computeIfAbsent(tabFor(key),k->new ArrayList<>()).add(item);
 }
 static final RegistryObject<Block> LAVA=BLOCKS.register("infinite_lava_generator",()->new InfiniteSource(Items.LAVA_BUCKET));
 static final RegistryObject<Block> WATER=BLOCKS.register("infinite_water_generator",()->new InfiniteSource(Items.WATER_BUCKET));
 static final RegistryObject<Item> LAVA_ITEM=ITEMS.register("infinite_lava_generator",()->new BlockItem(LAVA.get(),new Item.Properties()));
 static final RegistryObject<Item> WATER_ITEM=ITEMS.register("infinite_water_generator",()->new BlockItem(WATER.get(),new Item.Properties()));
 static final RegistryObject<Item> EIGHT=ITEMS.register("eight_bucket",EightBucket::new);
 static { for(String name:new String[]{"shaft","wooden_gear","iron_gear","steel_gear","gearbox","clutch","flywheel","bearing","chain_drive","belt_drive","differential","brake","hand_crank","water_wheel","wind_rotor","steam_engine","diesel_engine","electric_motor","generator","press","crusher","sawmill","lathe","drill_press","milling_machine","mixer","separator","pump","compressor","hydraulic_cylinder","pneumatic_cylinder","fluid_pipe","valve","fluid_tank","conveyor","item_sorter","robotic_arm","mechanical_hopper","automatic_crafter","furnace_burner","heat_exchanger","redstone_controller","speed_sensor","temperature_sensor","pressure_sensor","switchgear","elevator_motor","winch","pulley","mechanical_joint","rotary_table","gear_shifter","lubricator","oil_refinery","assembly_table","blueprint_table","mining_drill","harvester","mechanical_plough","rotary_sieve"}) part(name); TAB_ITEMS.add(LAVA_ITEM);TAB_ITEMS.add(WATER_ITEM);TAB_ITEMS.add(EIGHT); }
 static {
  // The 800 construction blocks are grouped by theme. Additional machines and buckets go into Main.
  Set<RegistryObject<Item>> assigned=new HashSet<>();
  GROUP_ITEMS.values().forEach(assigned::addAll);
  for(RegistryObject<Item> item:TAB_ITEMS)if(!assigned.contains(item))GROUP_ITEMS.get("main").add(item);
  for(String tab:TAB_NAMES)registerCreativeTab(tab);
 }
 public MechanicalUniverse() {
  IEventBus bus=FMLJavaModLoadingContext.get().getModEventBus();
  BLOCKS.register(bus);
  ITEMS.register(bus);
  CREATIVE_TABS.register(bus);
 }
 public static class InfiniteSource extends Block {
  private final Item output;
  public InfiniteSource(Item out){super(BlockBehaviour.Properties.copy(Blocks.IRON_BLOCK));output=out;}
  @Override public InteractionResult use(BlockState state,Level world,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
   ItemStack held=player.getItemInHand(hand);
   if(!held.is(Items.BUCKET))return InteractionResult.PASS;
   if(!world.isClientSide){if(!player.getAbilities().instabuild)held.shrink(1);ItemStack filled=new ItemStack(output);if(held.isEmpty())player.setItemInHand(hand,filled);else if(!player.getInventory().add(filled))player.drop(filled,false);}
   return InteractionResult.sidedSuccess(world.isClientSide);
  }
 }
 public static class EightBucket extends Item {
  public EightBucket(){super(new Item.Properties().stacksTo(1));}
  @Override public InteractionResult useOn(UseOnContext ctx){
   Level world=ctx.getLevel();ItemStack bucket=ctx.getItemInHand();BlockPos pos=ctx.getClickedPos();BlockState b=world.getBlockState(pos);
   String fluid=b.is(Blocks.WATER)?"water":b.is(Blocks.LAVA)?"lava":"";
   var nbt=bucket.getOrCreateTag();int count=nbt.getInt("Count");String stored=nbt.getString("Fluid");
   if(!fluid.isEmpty() && world.getFluidState(pos).isSource() && count<8 && (stored.isEmpty()||stored.equals(fluid))){
    if(!world.isClientSide){world.setBlock(pos,Blocks.AIR.defaultBlockState(),3);nbt.putString("Fluid",fluid);nbt.putInt("Count",count+1);}
    return InteractionResult.sidedSuccess(world.isClientSide);
   }
   BlockPos dest=pos.relative(ctx.getClickedFace());
   if(count>0 && world.getBlockState(dest).canBeReplaced() && !(stored.equals("water")&&world.dimensionType().ultraWarm())){
    if(!world.isClientSide){world.setBlock(dest,stored.equals("lava")?Blocks.LAVA.defaultBlockState():Blocks.WATER.defaultBlockState(),3);nbt.putInt("Count",count-1);if(count==1)nbt.remove("Fluid");}
    return InteractionResult.sidedSuccess(world.isClientSide);
   }
   return InteractionResult.PASS;
  }
  @Override public void appendHoverText(ItemStack stack,Level world,List<Component> tooltip,TooltipFlag flag){var t=stack.getTag();tooltip.add(Component.literal("Liquid: "+(t==null?"empty":t.getString("Fluid"))+"  "+(t==null?0:t.getInt("Count"))+"/8"));}
 }
}