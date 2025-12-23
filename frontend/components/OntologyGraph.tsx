import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Ontology } from '../types';

interface OntologyGraphProps {
  data: Ontology;
}

const OntologyGraph: React.FC<OntologyGraphProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const updateGraph = () => {
      const width = containerRef.current?.clientWidth || 800;
      const height = containerRef.current?.clientHeight || 600;

      // Clear previous graph
      d3.select(svgRef.current).selectAll("*").remove();

      const svg = d3.select(svgRef.current)
        .attr("viewBox", [0, 0, width, height]);

      const container = svg.append("g");

      // Zoom behavior
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
          container.attr("transform", event.transform);
        });

      svg.call(zoom);

      const simulation = d3.forceSimulation<any>(data.nodes)
        .force("link", d3.forceLink<any, any>(data.edges).id(d => d.id).distance(200))
        .force("charge", d3.forceManyBody().strength(-2000))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(60));

      const link = container.append("g")
        .attr("stroke", "rgba(59, 130, 246, 0.2)")
        .attr("stroke-width", 2)
        .selectAll("line")
        .data(data.edges)
        .join("line");

      const linkLabel = container.append("g")
        .selectAll("text")
        .data(data.edges)
        .join("text")
        .attr("fill", "rgba(255, 255, 255, 0.3)")
        .attr("font-size", "10px")
        .attr("text-anchor", "middle")
        .attr("font-weight", "900")
        .attr("class", "uppercase")
        .text(d => d.label);

      const node = container.append("g")
        .selectAll("g")
        .data(data.nodes)
        .join("g")
        .call(d3.drag<any, any>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }));

      node.append("circle")
        .attr("r", 32)
        .attr("fill", (d: any) => d.type === 'Class' ? "rgba(37, 99, 235, 0.1)" : "rgba(16, 185, 129, 0.1)")
        .attr("stroke", (d: any) => d.type === 'Class' ? "#3b82f6" : "#10b981")
        .attr("stroke-width", 3)
        .attr("class", "shadow-xl");

      node.append("text")
        .attr("dy", 50)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .attr("font-size", "11px")
        .attr("font-weight", "900")
        .attr("class", "uppercase italic tracking-widest")
        .text(d => d.label);

      simulation.on("tick", () => {
        link
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);

        linkLabel
          .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
          .attr("y", (d: any) => (d.source.y + d.target.y) / 2 - 8);

        node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
      });
    };

    updateGraph();

    // Resize observer for graph responsiveness
    const observer = new ResizeObserver(updateGraph);
    if (containerRef.current) observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, [data]);

  return (
    <div ref={containerRef} className="w-full h-full bg-black rounded-xl overflow-hidden relative">
      <svg ref={svgRef} className="w-full h-full" />
      <div className="absolute top-6 left-6 flex items-center gap-6">
        <div className="flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-blue-500"></div>
           <span className="text-[9px] font-black uppercase text-white/40 tracking-widest">Class Node</span>
        </div>
        <div className="flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
           <span className="text-[9px] font-black uppercase text-white/40 tracking-widest">Relation Hub</span>
        </div>
      </div>
      <div className="absolute bottom-6 right-6">
        <div className="bg-white/5 backdrop-blur-xl px-4 py-2 rounded-xl border border-white/5 text-[9px] font-black uppercase tracking-[0.2em] text-white/40">
          Interaction: Pan / Orbit / Focus
        </div>
      </div>
    </div>
  );
};

export default OntologyGraph;
